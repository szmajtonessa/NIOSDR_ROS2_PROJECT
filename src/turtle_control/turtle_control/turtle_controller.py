#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.srv import Spawn
from turtlesim.msg import Pose
import tkinter as tk

class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.window = tk.Tk()
        self.window.title("Turtle Control Interface")
        self.canvas = tk.Canvas(self.window, width=400, height=400, bg='white')
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def handle_click(self, event):
        canvas_height = self.canvas.winfo_height()
        middle = canvas_height / 2
        twist = Twist()

        # Draw a red rectangle at the clicked position
        rect_size = 10  # Size of the rectangle
        self.canvas.create_rectangle(event.x - rect_size, event.y - rect_size, 
                                      event.x + rect_size, event.y + rect_size, 
                                      outline="red", width=2)

        if event.y < middle:
            twist.linear.x = 2.0  # Move forward
            twist.angular.z = 0.0
            self.get_logger().info("Moving forward")
        else:
            twist.linear.x = -2.0  # Move backward
            twist.angular.z = 0.0
            self.get_logger().info("Moving backward")

        self.publisher_.publish(twist)

    def on_close(self):
        self.destroy_node()
        self.window.destroy()

    def run(self):
        self.window.mainloop()


def main(args=None):
    rclpy.init(args=args)

    # Create node and controller
    turtle_controller = TurtleController()

    # Ensure turtlesim is ready
    node = rclpy.create_node('turtle_spawner')
    client = node.create_client(Spawn, '/spawn')
    if not client.wait_for_service(timeout_sec=5.0):
        node.get_logger().error("Turtlesim service '/spawn' not available.")
        return

    # Spawn turtle if necessary
    request = Spawn.Request()
    request.x = 5.5
    request.y = 5.5
    request.theta = 0.0
    request.name = 'turtle1'
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)

    if future.result() is not None:
        node.get_logger().info(f"Turtle spawned: {future.result().name}")
    else:
        node.get_logger().error("Failed to spawn turtle.")

    node.destroy_node()

    # Run the turtle control interface
    try:
        turtle_controller.run()
    except KeyboardInterrupt:
        pass

    rclpy.shutdown()


if __name__ == '__main__':
    main()
