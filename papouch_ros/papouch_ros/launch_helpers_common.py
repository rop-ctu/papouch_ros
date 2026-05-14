import os
from typing import Optional
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
    Command,
    FindExecutable
)
from launch.substitution import Substitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import RegisterEventHandler, EmitEvent
from launch.events import Shutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.event_handlers import OnProcessExit

from typing import List

import launch.logging

from launch.action import Action
from launch.frontend import Entity
from launch.frontend import expose_action
from launch.frontend import Parser  # noqa: F401
from launch.launch_context import LaunchContext
from launch.some_substitutions_type import SomeSubstitutionsType
from launch.utilities import normalize_to_list_of_substitutions

__all__ = [
    "path_join",
    "SetupContext",
    "LogError",
    "parameter_value_xacro",
    "include_path_join",
    "remap_to_ns",
    "required_node",
]


def path_join(*items: str | Substitution, pkg: str) -> Substitution:
    """Join items into a path to a package share."""
    return PathJoinSubstitution([FindPackageShare(pkg), *items])


class SetupContext:
    def __init__(self, context: LaunchContext, pkg: Optional[str] = None):
        self.context = context
        self.pkg = pkg

    def config(self, name: str) -> str:
        return LaunchConfiguration(name).perform(self.context)

    def config_bool(self, name: str) -> bool:
        return LaunchConfiguration(name).perform(self.context).lower() == "true"

    def config_path(self, *items: str, pkg: Optional[str] = None,
                    allow_empty: bool = False,
                    check: Optional[str] = 'file',
                    ) -> Optional[Substitution]:
        """Create a path to a package share.

        The package name can be given as a keyword argument 'pkg', it
        defaults to this package.

        The last item of *items (can be the only one) is the name of the launch
        argument that is resolved. If there is a single item only, it is split
        to optional package name (overrides the 'pkg') and a list of path items
        given as 'pkg:path/to/file' or 'path/to/file'.

        The list of items is then joined with the package share path.

        When allow_empty is True and the last item (after resolving) is empty,
        None is returned.
        """

        if pkg is None:
            pkg = self.pkg

        items = list(items)  # copy to avoid modifying the original list
        name = items[-1]
        items[-1] = LaunchConfiguration(name).perform(self.context)

        if items[-1] == "":
            if allow_empty:
                return None
            else:
                raise RuntimeError(f"Empty value of LaunchConfiguration {name}")

        if len(items) == 1:
            # try to split the item into an optional package name and a path
            if ":" in items[0]:
                pkg, items[0] = items[0].split(":", 1)

            items = items[0].split("/")

        assert (pkg is not None)
        pth_subst = path_join(*items, pkg=pkg)
        if check == 'file':
            pth = pth_subst.perform(self.context)
            # check for file existence
            if not os.path.isfile(pth):
                raise RuntimeError(f"LaunchConfiguration '{name}': path does " +
                                   f"not exist ({pth})")

        return pth_subst


@expose_action('log_error')
class LogError(Action):
    """Action that logs a message when executed."""

    def __init__(self, *, msg: SomeSubstitutionsType, **kwargs):
        """Create a LogInfo action."""
        super().__init__(**kwargs)

        self.__msg = normalize_to_list_of_substitutions(msg)
        self.__logger = launch.logging.get_logger('launch.user')

    @classmethod
    def parse(
            cls,
            entity: Entity,
            parser: 'Parser'
    ):
        """Parse `log` tag."""
        _, kwargs = super().parse(entity, parser)
        kwargs['msg'] = parser.parse_substitution(entity.get_attr('message'))
        return cls, kwargs

    @property
    def msg(self) -> List[Substitution]:
        """Getter for self.__msg."""
        return self.__msg

    def execute(self, context: LaunchContext) -> None:
        """Execute the action."""
        self.__logger.error(
            ''.join([context.perform_substitution(sub) for sub in self.msg])
        )
        return None


def parameter_value_xacro(
        xacro_file_substitution: Substitution,
        xacro_args: dict | None = None) -> ParameterValue:
    """Apply xacro command to a xacro file with arguments."""

    if xacro_args is not None:
        params = [arg
                  for key, val in xacro_args.items()
                  for arg in (f" {key}:=", val)]
    else:
        params = []

    return ParameterValue(
        Command(
            [
                PathJoinSubstitution([FindExecutable(name="xacro")]),
                " ",
                xacro_file_substitution,
                # Convert dict to list of parameters
                *params,
            ]
        ),
        value_type=str,
    )


def include_path_join(*items: str, pkg: str,
                      launch_arguments=None) -> IncludeLaunchDescription:
    """Join items into a path to a package share and include as launch description ."""

    if launch_arguments is None:
        launch_arguments = []

    if isinstance(launch_arguments, dict):
        launch_arguments = [launch_arguments]

    args = {}
    # go through arguments, latter overwrites former
    for arg in launch_arguments:
        if isinstance(arg, dict):
            for k in arg:
                args[k] = arg[k]
        elif isinstance(arg, tuple):
            args[arg[0]] = arg[1]
        elif isinstance(arg, DeclareLaunchArgument):
            args[arg.name] = LaunchConfiguration(arg.name)
        else:
            raise RuntimeError(f"Unhandled lauch argument {arg}")

    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource([path_join(*items, pkg=pkg)]),
        launch_arguments=args.items())


def remap_to_ns(ns, *items: str):
    return [(f"/{item}", f"/{ns}/{item}") for item in items]


def required_node(node: Node) -> tuple[Node, RegisterEventHandler]:
    """Helper function to register an event handler to log an error if a
     required node exits.
     :returns: A tuple of the original node and the event handler.
     """
    handler = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=node,
            on_exit=[
                LogError(
                    msg=f"Required node exited: {node.node_package}/{node.node_executable}"),
                EmitEvent(event=Shutdown())]))

    return node, handler
