#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

# for python API, see <https://carla.readthedocs.io/en/latest/python_api/>

import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
# import cv2
from PIL import Image
import numpy as np

import random
import time

import pygame

TOWN = 'Town04'

def my_display(display, image):
    try:
        # image.save_to_disk('_out/%1d_%06d.png' % (0, image.frame))
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]
        surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        display.blit(surface, (0, 0))
        # hud.render(display)
        pygame.display.flip()
    except Exception:
        print ('err')

def main():
    actor_list = []
    # pygame
    pygame.init()
    pygame.font.init()
    display = pygame.display.set_mode(
            (1080, 1080),
            pygame.HWSURFACE | pygame.DOUBLEBUF)
    # hud = HUD(1080, 1080)
    
    # In this tutorial script, we are going to add a vehicle to the simulation
    # and let it drive in autopilot. We will also create a camera attached to
    # that vehicle, and save all the images generated by the camera to disk.

    try:
        # First of all, we need to create the client that will send the requests
        # to the simulator. Here we'll assume the simulator is accepting
        # requests in the localhost at port 2000.
        client = carla.Client('localhost', 2000)
        client.set_timeout(4.0)
        # world = client.load_world(TOWN)
        # Once we have a client we can retrieve the world that is currently
        # running.
        world = client.get_world()
        world.set_weather(carla.WeatherParameters(sun_azimuth_angle=30.0, sun_altitude_angle=30.0,
                                                    wind_intensity =30.0))
        # return
        old_vehicles = world.get_actors().filter('vehicle.*')
        for actor in old_vehicles:
            actor.destroy()
        # The world contains the list blueprints that we can use for adding new
        # actors into the simulation.
        blueprint_library = world.get_blueprint_library()

        # Now let's filter all the blueprints of type 'vehicle' and choose one
        # at random.
        bp = random.choice(blueprint_library.filter('audi'))

        # A blueprint contains the list of attributes that define a vehicle's
        # instance, we can read them and modify some of them. For instance,
        # let's randomize its color.
        if bp.has_attribute('color'):
            color = random.choice(bp.get_attribute('color').recommended_values)           
            # color = carla.Color(r=255, b =100, g =30)
            bp.set_attribute('color', '255,50,50')

        # Now we need to give an initial transform to the vehicle. We choose a
        # random transform from the list of recommended spawn points of the map.
        spawn_point = carla.Transform(carla.Location(x=-120.4, y=13.0, z=10), 
		                carla.Rotation(pitch=0, yaw=180, roll=0))

        # transform = random.choice(world.get_map().get_spawn_points())
        # transform.location = carla.Location(x=24, y=10)
        # transform.rotation = carla.Rotation(0,0,0)

        # So let's tell the world to spawn the vehicle.
        vehicle = world.spawn_actor(bp, spawn_point)
        vehicle.apply_control(carla.VehicleControl(throttle=0.0, steer=0.0, brake=1.0))

        # It is important to note that the actors we create won't be destroyed
        # unless we call their "destroy" function. If we fail to call "destroy"
        # they will stay in the simulation even after we quit the Python script.
        # For that reason, we are storing all the actors we create so we can
        # destroy them afterwards.
        actor_list.append(vehicle)
        print('created %s' % vehicle.type_id)

        if bp.has_attribute('color'):
            # color = carla.Color(r= 30, b = 30, g = 30)
            bp.set_attribute('color', '30,30,30')
        spawn_point = carla.Transform(carla.Location(x=-120.4, y=15.6, z=10), 
		                carla.Rotation(pitch=0, yaw=180, roll=0))
        vehicle2 = world.spawn_actor(bp, spawn_point)
        vehicle2.apply_control(carla.VehicleControl(throttle=0.3, steer=0.12, brake=0.0))
        # It is important to note that the actors we create won't be destroyed
        # unless we call their "destroy" function. If we fail to call "destroy"
        # they will stay in the simulation even after we quit the Python script.
        # For that reason, we are storing all the actors we create so we can
        # destroy them afterwards.
        actor_list.append(vehicle2)
        print('created %s' % vehicle.type_id)

        # Let's put the vehicle to drive around.
        # vehicle.set_autopilot(True)

        # Let's add now a "depth" camera attached to the vehicle. Note that the
        # transform we give here is now relative to the vehicle.
        for i in range(2):
            camera_bp = blueprint_library.find('sensor.camera.rgb')
            camera_bp.set_attribute('image_size_x', '1080')
            camera_bp.set_attribute('image_size_y', '1080')
            # camera_bp.set_attribute('lens_circle_falloff', '0.1')
            camera_bp.set_attribute('lens_circle_multiplier', '0')
            camera_bp.set_attribute('lens_circle_multiplier', '0')
            camera_bp.set_attribute('fov', '120')    
            camera_bp.set_attribute('lens_k', '0.0')
            # camera_bp.set_attribute('disable_distortion', '1')
            
            # camera.set(FOV=90.0)
            # camera.set_image_size(800, 600)
            if i==0:
                # camera.listen(lambda image: image.save_to_disk('_out/%1d_%06d.png' % (0, image.frame)))
                camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
                camera_transform.rotation.yaw = i * -75.0
                camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
                print('0')
                # camera.listen(lambda image: my_display(display, image))
            else:
                # camera.listen(lambda image: image.save_to_disk('_out/%1d_%06d.png' % (1, image.frame)))
                camera_transform = carla.Transform(carla.Location(x=1.5, z=1.2, y=-0.8))
                camera_transform.rotation.yaw = i * -75.0
                camera_transform.rotation.pitch = -15
                camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
                camera.listen(lambda image: my_display(display, image))
                # print('5')
            actor_list.append(camera)
            print('created %s_%1d' % (camera.type_id, i))
            

        # Now we register the function that will be called each time the sensor
        # receives an image. In this example we are saving the image to disk
        # converting the pixels to gray-scale.
        cc = carla.ColorConverter.LogarithmicDepth
        # camera.listen(lambda image: image.save_to_disk('_out/%06d.png' % image.frame, cc))
        # camera.listen(lambda image: image.save_to_disk('_out/%06d.png' % image.frame))
        # camera.listen(lambda image: print(type(image)))

        # Oh wait, I don't like the location we gave to the vehicle, I'm going
        # to move it a bit forward.
        # location = vehicle.get_location()
        # location.x += 40
        # location = carla.Location(x=20, y=10)
        # vehicle.set_location(location)
        # vehicle.set_location(location)
        # print('moved vehicle to %s' % location)

        # But the city now is probably quite empty, let's add a few more
        # vehicles.
        # transform.location += location
        # transform.rotation.yaw = -90.0
        # for _ in range(0, 10):
        #     location = vehicle.get_location()
        #     location.y -= 1.0
            # vehicle.set_location(location)

        #     bp = random.choice(blueprint_library.filter('vehicle'))

        #     # This time we are using try_spawn_actor. If the spot is already
        #     # occupied by another object, the function will return None.
        #     npc = world.try_spawn_actor(bp, transform)
        #     if npc is not None:
        #         actor_list.append(npc)
        #         npc.set_autopilot()
        #         print('created %s' % npc.type_id)
            # time.sleep(1)
        state = 0
        while True:
            time.sleep(0.5)
            location = vehicle2.get_location()
            if(state == 0):
                if(location.y -1 < vehicle.get_location().y):
                    vehicle2.apply_control(carla.VehicleControl(throttle=0.3, steer=-0.1, brake=0.0))
                    state = 1
            if(state == 1):
                yaw = vehicle2.get_transform().rotation.yaw               
                if((yaw < 0 and yaw <= -180 ) or (yaw > 0 and yaw <= 180) ):
                    vehicle2.apply_control(carla.VehicleControl(throttle=0.7, steer=0.0, brake=0.0))
                    state = 2
            
            if(state == 2):
                time.sleep(4)
                break

    finally:

        print('destroying actors')
        for actor in actor_list:
            actor.destroy()
        print('done.')


if __name__ == '__main__':

    main()