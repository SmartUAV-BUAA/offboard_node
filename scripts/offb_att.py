
#!/usr/bin/env python

import rospy
#from geometry_msgs.msg import *
import geometry_msgs.msg as geo_msgs
from mavros_msgs.srv import CommandBool
from mavros_msgs.srv import SetMode
from mavros_msgs.msg import State

VEL_fLAG = 0
current_state = State()

def state_cb(msg_temp):
	global current_state
	current_state = msg_temp
	#print("current state:", current_state)
	print("callback")

if __name__=="__main__":
	#global current_state
	rospy.init_node('offb_node', anonymous=True)
	rospy.Subscriber("mavros/state", State, state_cb)
	local_pos_pub = rospy.Publisher('mavros/setpoint_position/local', geo_msgs.PoseStamped, queue_size=10)
	if(VEL_fLAG ==1):
		local_vel_pub = rospy.Publisher('mavros/setpoint_velocity/cmd_vel', geo_msgs.Twist, queue_size=10)

	print("Publisher and Subscriber Created")
	arming_client = rospy.ServiceProxy('mavros/cmd/arming', CommandBool)
	set_mode_client = rospy.ServiceProxy('mavros/set_mode', SetMode)
	print("Clients Created")
	rate = rospy.Rate(20)
	
	while(not current_state.connected):
		#print("current_state.connected: ",current_state.connected)
		rate.sleep()
	
	print("Creating pose")
	pose = geo_msgs.PoseStamped()
	#set position here
	pose.pose.position.x = 0
	pose.pose.position.y = 0
	pose.pose.position.z = 20

	if(VEL_fLAG ==1):
		vel = geo_msgs.Twist()
		vel.linear.x = 20
		vel.linear.y = 20
		vel.linear.z = 20
	
	# for i in range(100):
	# 	local_pos_pub.publish(pose)
	# 	rate.sleep()
	# 	print("i=",i)
		
	print("Creating Objects for services")
	offb_set_mode = SetMode()
	offb_set_mode.custom_mode = "OFFBOARD"
	arm_cmd = CommandBool()
	arm_cmd.value = True
	
	last_request = rospy.Time.now()
	
	while not rospy.is_shutdown():
		#print(current_state)
		if(current_state.mode != "OFFBOARD" and (rospy.Time.now() - last_request > rospy.Duration(5.0))):
			resp1 = set_mode_client(0,offb_set_mode.custom_mode)
			if resp1.mode_sent:
				print ("Offboard enabled")
			last_request = rospy.Time.now()
		elif (not current_state.armed and (rospy.Time.now() - last_request > rospy.Duration(5.0))):
			arm_client_1 = arming_client(arm_cmd.value)
			if arm_client_1.success:
				print("Vehicle armed")
			last_request = rospy.Time.now()
			
		local_pos_pub.publish(pose)
		if(VEL_fLAG == 1):
			local_vel_pub.publish(vel)
		#print current_state
		rate.sleep()