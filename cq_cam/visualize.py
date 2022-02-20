import logging

from OCP.AIS import AIS_MultipleConnectedInteractive, AIS_Line, AIS_Shape
from OCP.Geom import Geom_CartesianPoint
from cadquery import cq, Edge
from cq_editor.cq_utils import to_occ_color

from cq_cam.commands.base_command import MotionCommand
from cq_cam.commands.command import Plunge, Cut, Rapid, Circular
from cq_cam.commands.util_command import arc_center_midpoint
from cq_cam.job import Job
from cq_cam.operations.base_operation import Task

logger = logging.getLogger(__name__)


class VisualizeError(Exception):
    pass


def visualize_task(job: Job, task: Task):
    root_workplane = job.workplane
    root_plane = root_workplane.plane

    group = AIS_MultipleConnectedInteractive()

    # x = 0
    # y = 0
    # z = job.rapid_height
    start = cq.Vector(0, 0, job.rapid_height)

    last_plunge = True
    for command in task.commands:
        if isinstance(command, MotionCommand):
            end = command.end(start)
            # cx = command.end.x
            # cy = command.end.y
            # cz = command.end.z

            # New viz method coords are in world
            world_start = root_plane.toWorldCoords((start.x, start.y, start.z))
            world_end = root_plane.toWorldCoords((end.x, end.y, end.z))
            #world_start = start
            #world_end = end
            if isinstance(command, Circular):

                # W
                try:
                    if command.mid:
                        midpoint = cq.Vector(command.mid)
                    else:
                        _, midpoint = arc_center_midpoint(command, start, end)

                    # radius = command.radius if isinstance(command, CircularCW) else -command.radius
                    # wp = (
                    #    root_workplane.workplane(offset=start.z)
                    #        .moveTo(start.x, start.y)
                    #        .radiusArc((end.x, end.y), radius)
                    # )

                    arc = Edge.makeThreePointArc(world_start,
                                                 root_plane.toWorldCoords((midpoint.x, midpoint.y, midpoint.z)),
                                                 world_end)
                    # line = AIS_Shape(wp.objects[0].wrapped)
                    line = AIS_Shape(arc.wrapped)
                except:
                    line = AIS_Line(
                        Geom_CartesianPoint(world_start.x, world_start.y, world_start.z),
                        Geom_CartesianPoint(world_end.x, world_end.y, world_end.z)
                    )
                    line.SetColor(to_occ_color('yellow'))
            else:
                if world_start == world_end:
                    logger.warning("encountered zero length")
                    continue
                line = AIS_Line(
                    Geom_CartesianPoint(world_start.x, world_start.y, world_start.z),
                    Geom_CartesianPoint(world_end.x, world_end.y, world_end.z)
                )
                print(line)
            if isinstance(command, Rapid):
                line.SetColor(to_occ_color('green'))
            elif isinstance(command, Cut):
                line.SetColor(to_occ_color('red'))
            elif isinstance(command, Plunge):
                line.SetColor(to_occ_color('blue'))

            if isinstance(command, Plunge):
                line.Attributes().SetLineArrowDraw(True)
                last_plunge = True
            elif last_plunge and isinstance(line, AIS_Line):
                line.Attributes().SetLineArrowDraw(True)
                last_plunge = False

            group.Connect(line)

            start = end

    return group
