    #!/usr/bin/env python

"""
Listens on 'write_traj' topic for a trajectory message, and publishes the corresponding 
trajectory with markers on the 'visualization_markers' topic, as an animation.

Trajectory coordinates are published in the 'paper_sheet' frame. You may want to first
broadcast it.
"""

import logging
logger = logging.getLogger("write." + __name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(name)s -> %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

import rospy
from visualization_msgs.msg import Marker
from nav_msgs.msg import Path

FRAME = "writing_surface"
WRITE_MULTIPLE_SHAPES = True;       #if True, modify the marker ID so as to not overwrite the previous shape

pub_markers = rospy.Publisher('visualization_marker', Marker);

rospy.init_node("trajectory_visualiser");

def visualize_traj(points):

    traj = Marker()
    traj.header.frame_id = FRAME
    traj.header.stamp = rospy.get_rostime()
    traj.ns = "love_letter"
    traj.action = Marker.ADD
    traj.pose.orientation.w = 1.0
    traj.type = Marker.LINE_STRIP
    traj.scale.x = 0.001 # line width
    traj.color.r = 1.0
    traj.color.b = 0.0
    traj.color.a = 1.0
    
    if(WRITE_MULTIPLE_SHAPES):
        traj.id = shapeCount;
    else:
        traj.id = 0; #overwrite any existing shapes
        traj.lifetime.secs = 1; #timeout for display
    
    traj.points = list(points)
    
    # use interactive marker from place_paper instead
    #pub_markers.publish(a4_sheet()) 
    pub_markers.publish(traj)

def on_traj(requested_traj):
    global shapeCount #@todo find out how to pass this with callback..
    written_points = []
    print("got traj at "+str(rospy.Time.now()))   
    
    #wait until time instructed to start executing
    rospy.sleep(requested_traj.header.stamp-rospy.Time.now());
    print("executing traj at "+str(rospy.Time.now())) 
    startTime = rospy.Time.now();
    #wait for robot to get to starting point
    rospy.sleep(requested_traj.poses[0].header.stamp.to_sec()); 

    #add points to the display one at a time, like an animation
    for i in range(len(requested_traj.poses)-1): 
        p = requested_traj.poses[i].pose.position;
        written_points.append(p)
        visualize_traj(written_points)
        duration = requested_traj.poses[i+1].header.stamp - requested_traj.poses[i].header.stamp;
        rospy.sleep(duration); #wait until it's time to show the next point
        
    #show final point (no sleep afterwards, but it does have a "lifetime" set in visualize_traj)    
    p = requested_traj.poses[len(requested_traj.poses)-1].pose.position;
    written_points.append(p)
    visualize_traj(written_points)
    print("Time taken for whole trajectory: "+str((rospy.Time.now()-startTime).to_sec()));
    shapeCount += 1;

shapeCount = 0;
#when we get a trajectory, start publishing the animation
pub_traj = rospy.Subscriber('write_traj', Path, on_traj)
rospy.spin()
