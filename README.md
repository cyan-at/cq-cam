cam algorithms are easy, amrite?

```
box = cq.Workplane().box(10, 10, 10)
box_top = box.faces('>Z').workplane()

job = Job(workplane=box_top, feed=300, plunge_feed=50, unit=Unit.METRIC, rapid_height=10)
profile = Profile(job=job, clearance_height=5, top_height=0, wire=box.wires('<Z'), offset=3.175 / 2, stepdown=-2.77)

print(job.to_gcode())

visual_toolpaths = visualize_task(job, profile)
show_object(box, 'box')
show_object(visual_toolpaths, 'visual_toolpaths',)
```
