# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 10:58:30 2019

@author: Jakub Grzeszczak
"""
import pygame, sys, math, numpy, os, shutil, pygame.gfxdraw

class View_model_generator:
    class Polyhedron:
        def __init__(self, filename="data.txt"):
            self.vert_count = -1
            self.edge_count = -1
            self.face_count = -1
            self.vertices = None
            self.edge = None
            self.face = None
            self.sphere_radius = None
            self.polyhedron = None
            self.load_from_file(filename)
            
        def load_from_file(self,filename="data.txt"):
            """
            wczytuje dane z pliku i centruje powstałą bryłę lokalnie w punkcie (0,0,0)
            """
            try:
                with open(filename, "r") as file:
                    self.vert_count = int(file.readline())
                    if(self.vert_count >0):
                        self.vertices = []
                    else:
                        print("bad input")
                        sys.exit()
                    for i in range(self.vert_count):
                        line = file.readline()
                        self.vertices.append(tuple(float(x) for x in line.split()))
                    self.edge_count = int(file.readline())
                    if(self.edge_count >0):
                        self.edges = []
                    else:
                        print("bad input")
                        sys.exit()
                    for i in range(self.edge_count):
                        line = file.readline()
                        self.edges.append(tuple(sorted(int(x) for x in line.split())))
                    self.face_count = int(file.readline())
                    if(self.face_count >0):
                        self.faces = []
                    else:
                        print("bad input")
                        sys.exit()
                    for i in range(self.face_count):
                        line = file.readline()
                        self.faces.append(tuple(int(x) for x in line.split()))
                    
                    #centrowanie bryły
                    avgx, avgy, avgz = 0.0, 0.0, 0.0
                    for i in range(0, self.vert_count):
                        avgx += self.vertices[i][0]
                        avgy += self.vertices[i][1]
                        avgz += self.vertices[i][2]
                    avgx /= self.vert_count
                    avgy /= self.vert_count
                    avgz /= self.vert_count
                    self.vertices = [(v[0]-avgx, v[1]-avgy, v[2]-avgz) for v in self.vertices]
                    print('Konieczne przesunięcie bryły o wektor:', avgx,avgy,avgz)
                    self.sphere_radius = 0
                    for vert in self.vertices:
                        temp_radius = math.sqrt(vert[0]**2 + vert[1]**2 + vert[2]**2)
                        if self.sphere_radius < temp_radius:
                            self.sphere_radius = temp_radius
                    return True
                    
            except IOError as e:
                print("I/O error({0}): {1}".format(e.errno, e.strerror))
                print("replacing data with default parameters")
                self.sphere_radius = 1.0
                self.vert_count = 8
                self.edge_count = 12
                self.face_count = 6
                self.vertices = (0,1,-1),(-1,1,0),(0,1,1),(1,1,0),(0,-1,-1),(-1,-1,0),(0,-1,1),(1,-1,0),
                self.edges = (0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5 , 6), (6 , 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)
                self.faces = (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (0, 3, 7, 4), (1, 2, 6, 5)
                return False
            
        def get_centered_on_point(self,index):
            axis = [(1,0,0),(2,0,0),(0,1,0),(0,2,0),(0,0,1),(0,0,2),(-1,0,0),(-2,0,0),(0,-1,0),(0,-2,0),(0,0,-1),(0,0,-2)]
            x,y,z = self.vertices[index]
            x_angle = math.atan2(y,z)
            x_target_angle = math.radians(180)
            x_rot_angle = x_target_angle - x_angle
            cos_angle_ox = math.cos(x_rot_angle)
            sin_angle_ox = math.sin(x_rot_angle)
            ox_matrix = [[1.0,    0.0,    0.0],
                         [0.0,    cos_angle_ox,     -sin_angle_ox], 
                         [0.0,    sin_angle_ox,    cos_angle_ox]]
            x,y,z = numpy.matmul((x,y,z),ox_matrix)
            y_angle = math.atan2(z,x)
            y_target_angle = math.radians(-90)
            y_rot_angle = y_target_angle - y_angle
            cos_angle_oy = math.cos(y_rot_angle)
            sin_angle_oy = math.sin(y_rot_angle)
            oy_matrix = [[cos_angle_oy, 0.0, sin_angle_oy],
                         [0.0,    1.0,    0.0], 
                         [-sin_angle_oy,    0.0,    cos_angle_oy]]
            x,y,z = numpy.matmul((x,y,z),oy_matrix)
            verts = []
            for vert in self.vertices:
                new_vert = numpy.matmul(vert,  ox_matrix)
                new_vert = numpy.matmul(new_vert,  oy_matrix)
                verts.append(new_vert)
            ax = []
            for vert in axis:
                new_vert = numpy.matmul(vert,  ox_matrix)
                new_vert = numpy.matmul(new_vert,  oy_matrix)
                ax.append(new_vert)
            return ax, verts
        
        def get_centered_on_edge(self,index):
            axis = [(1,0,0),(2,0,0),(0,1,0),(0,2,0),(0,0,1),(0,0,2),(-1,0,0),(-2,0,0),(0,-1,0),(0,-2,0),(0,0,-1),(0,0,-2)]
            points = [self.vertices[i] for i in self.edges[index]]
            
            x,y,z = (points[0][0]+points[1][0])/2,(points[0][1]+points[1][1])/2,(points[0][2]+points[1][2])/2
            x_angle = math.atan2(y,z)
            x_target_angle = math.radians(180)
            x_rot_angle = x_target_angle - x_angle
            cos_angle_ox = math.cos(x_rot_angle)
            sin_angle_ox = math.sin(x_rot_angle)
            ox_matrix = [[1.0,    0.0,    0.0],
                         [0.0,    cos_angle_ox,     -sin_angle_ox], 
                         [0.0,    sin_angle_ox,    cos_angle_ox]]
            x,y,z = numpy.matmul((x,y,z),ox_matrix)
            y_angle = math.atan2(z,x)
            y_target_angle = math.radians(-90)
            y_rot_angle = y_target_angle - y_angle
            cos_angle_oy = math.cos(y_rot_angle)
            sin_angle_oy = math.sin(y_rot_angle)
            oy_matrix = [[cos_angle_oy, 0.0, sin_angle_oy],
                         [0.0,    1.0,    0.0], 
                         [-sin_angle_oy,    0.0,    cos_angle_oy]]
            
            x,y,z = numpy.matmul(points[0], ox_matrix)
            x,y,z = numpy.matmul((x,y,z), oy_matrix)
            z_angle = math.atan2(y,-x)
            z_target_angle = math.radians(90)
            z_rot_angle = z_target_angle - z_angle
            cos_angle_oz = math.cos(z_rot_angle)
            sin_angle_oz = math.sin(z_rot_angle)
            oz_matrix = [[cos_angle_oz,    -sin_angle_oz,    0.0],
                         [sin_angle_oz,    cos_angle_oz,     0.0], 
                         [0.0,    0.0,    1.0]]
            verts = []
            for vert in self.vertices:
                new_vert = numpy.matmul(vert,  ox_matrix)
                new_vert = numpy.matmul(new_vert,  oy_matrix)
                new_vert = numpy.matmul(new_vert,  oz_matrix)
                verts.append(new_vert)
            ax = []
            for vert in axis:
                new_vert = numpy.matmul(vert,  ox_matrix)
                new_vert = numpy.matmul(new_vert,  oy_matrix)
                new_vert = numpy.matmul(new_vert,  oz_matrix)
                ax.append(new_vert)
            return ax, verts
        
        def get_centered_on_face(self,index):
            axis = [(1,0,0),(2,0,0),(0,1,0),(0,2,0),(0,0,1),(0,0,2),(-1,0,0),(-2,0,0),(0,-1,0),(0,-2,0),(0,0,-1),(0,0,-2)]
            verts = [self.vertices[i] for i in self.faces[index]]
            x,y,z = 0,0,0
            for vert in verts:
                x += vert[0]
                y += vert[1]
                z += vert[2]
            x /= len(self.faces[index])
            y /= len(self.faces[index])
            z /= len(self.faces[index])
            
            x_angle = math.atan2(y,z)
            x_target_angle = math.radians(180)
            x_rot_angle = x_target_angle - x_angle
            cos_angle_ox = math.cos(x_rot_angle)
            sin_angle_ox = math.sin(x_rot_angle)
            ox_matrix = [[1.0,    0.0,    0.0],
                         [0.0,    cos_angle_ox,     -sin_angle_ox], 
                         [0.0,    sin_angle_ox,    cos_angle_ox]]
            x,y,z = numpy.matmul((x,y,z),ox_matrix)
            y_angle = math.atan2(z,x)
            y_target_angle = math.radians(-90)
            y_rot_angle = y_target_angle - y_angle
            cos_angle_oy = math.cos(y_rot_angle)
            sin_angle_oy = math.sin(y_rot_angle)
            oy_matrix = [[cos_angle_oy, 0.0, sin_angle_oy],
                         [0.0,    1.0,    0.0], 
                         [-sin_angle_oy,    0.0,    cos_angle_oy]]
            
            x,y,z = (verts[0][0]+verts[1][0])/2,(verts[0][1]+verts[1][1])/2,(verts[0][2]+verts[1][2])/2
            x,y,z = numpy.matmul((x,y,z), ox_matrix)
            x,y,z = numpy.matmul((x,y,z), oy_matrix)
            z_angle = math.atan2(y,-x)
            z_target_angle = math.radians(90)
            z_rot_angle = z_target_angle - z_angle
            cos_angle_oz = math.cos(z_rot_angle)
            sin_angle_oz = math.sin(z_rot_angle)
            oz_matrix = [[cos_angle_oz,    -sin_angle_oz,    0.0],
                         [sin_angle_oz,    cos_angle_oz,     0.0], 
                         [0.0,    0.0,    1.0]]
            verts = []
            for vert in self.vertices:
                new_vert = numpy.matmul(vert,  ox_matrix)
                new_vert = numpy.matmul(new_vert,  oy_matrix)
                new_vert = numpy.matmul(new_vert,  oz_matrix)
                verts.append(new_vert)
            ax = []
            for vert in axis:
                new_vert = numpy.matmul(vert,  ox_matrix)
                new_vert = numpy.matmul(new_vert,  oy_matrix)
                new_vert = numpy.matmul(new_vert,  oz_matrix)
                ax.append(new_vert)
            return ax, verts
        
    def __init__(self):
        pygame.init()
        self.window_width = 501
        self.window_height = 501
        self.polyhedron = self.Polyhedron()
        self.alpha = math.radians(32)
        print("Parametry zadania:")
        print("kąt między wysokoscią a tworzącą stożka widzenia:", math.degrees(self.alpha))
        print("promień sfery opinającej bryłę:", self.polyhedron.sphere_radius)
        print("promień sfery widokowej:",self.polyhedron.sphere_radius/math.sin(self.alpha))
        self.screen = pygame.display.set_mode((self.window_width+100, self.window_height+100))
        self.main()
        
    def generate(self, axis, displayed_vertices, save_filename):
        if displayed_vertices == None:
            return
        # przygotowanie zmiennych
        cx = self.window_width//2 +50
        cy = self.window_height//2 +50
        R = self.polyhedron.sphere_radius/math.sin(self.alpha)
        self.POV = (0, 0, -R)
        D = (self.window_width//2)/math.tan(self.alpha) # odległosc punktu widokowego od ekranu
        font_48 = pygame.font.Font(None, 48)
        font_32 = pygame.font.Font(None, 32)
        font_24 = pygame.font.Font(None, 24)
        # pobranie danych o widoku
        border_id_edges, border_edges, visible_faces, not_visible_faces, border_visible_faces, border_not_visible_faces, face_normal_angles = self.calculate_view_area(displayed_vertices)
        self.screen.fill((250,250,250))
        #rysowanie sfery jednostkowej
        pygame.gfxdraw.aacircle(self.screen, cx, cy, 250, (0,0,0))
        #rysowanie osi współrzędnych z tyłu bryły
        
        ax = ('x+','y+','z+','x-','y-','z-')
        ax_colors = [(255,0,0),(0,0,255),(0,255,0),(255,0,0),(0,0,255),(0,255,0)]
        for i in range(0,6):
            depth = axis[i*2+1][2] - axis[i*2][2]
            if depth >= 0:
                x,y,z = axis[i*2]
                x2,y2,z2 = axis[i*2+1]
                d = z - self.POV[2]
                scalar = D/d # skalar wynikający z tw. Talesa
                XP = int(cx + x*scalar)
                YP = int(cy - y*scalar)
                d2 = z2 - self.POV[2]
                scalar = D/d # skalar wynikający z tw. Talesa
                XK = int(cx + x2*scalar)
                YK = int(cy - y2*scalar)
                pygame.gfxdraw.line(self.screen, XP,YP,XK,YK, ax_colors[i])
                ax_text = font_24.render(ax[i],True, ax_colors[i])
                self.screen.blit(ax_text,(XK,YK-16))
        # rysowanie bryły
        for face_id in visible_faces:
            coords = []
            vert_ids = []
            face_x, face_y = 0,0
            for vert_id in self.polyhedron.faces[face_id]:
                x,y,z = displayed_vertices[vert_id]
                vert_ids.append(vert_id)
                d = z - self.POV[2]
                scalar = D/d # skalar wynikający z tw. Talesa
                X = cx + x*scalar
                Y = cy - y*scalar
                face_x += X
                face_y += Y
                coords.append((X,Y))
            face_x, face_y = face_x/len(self.polyhedron.faces[face_id]), face_y/len(self.polyhedron.faces[face_id])
            coords.append(coords[0])
            vert_ids.append(vert_ids[0])
            pygame.gfxdraw.filled_polygon(self.screen, coords, (127,127,127))
            pygame.draw.polygon(self.screen, (20,20,20), coords, 1)
            pygame.gfxdraw.aapolygon(self.screen, coords, (20,20,20))
        
        #rysowanie osi współrzędnych przed bryłą
        
        ax = ('x+','y+','z+','x-','y-','z-')
        ax_colors = [(255,0,0),(0,0,255),(0,255,0),(255,0,0),(0,0,255),(0,255,0)]
        for i in range(0,6):
            depth = axis[i*2+1][2] - axis[i*2][2]
            if depth < 0:
                x,y,z = axis[i*2]
                x2,y2,z2 = axis[i*2+1]
                d = z - self.POV[2]
                scalar = D/d # skalar wynikający z tw. Talesa
                XP = int(cx + x*scalar)
                YP = int(cy - y*scalar)
                d2 = z2 - self.POV[2]
                scalar = D/d # skalar wynikający z tw. Talesa
                XK = int(cx + x2*scalar)
                YK = int(cy - y2*scalar)
                pygame.gfxdraw.line(self.screen, XP,YP,XK,YK, ax_colors[i])
                ax_text = font_24.render(ax[i],True, ax_colors[i])
                self.screen.blit(ax_text,(XK,YK-16)) 
        #opisywanie widoku bryły
        for face_id in visible_faces:
            coords = []
            vert_ids = []
            face_x, face_y = 0,0
            for vert_id in self.polyhedron.faces[face_id]:
                x,y,z = displayed_vertices[vert_id]
                vert_ids.append(vert_id)
                d = z - self.POV[2]
                scalar = D/d # skalar wynikający z tw. Talesa
                X = cx + x*scalar
                Y = cy - y*scalar
                face_x += X
                face_y += Y
                coords.append((X,Y))
            face_x, face_y = face_x/len(self.polyhedron.faces[face_id]), face_y/len(self.polyhedron.faces[face_id])
            coords.append(coords[0])
            vert_ids.append(vert_ids[0])
            for id in range(len(coords)):
                x,y = coords[id]
                if x < cx:
                    x -= 8
                if y < cy:
                    y -= 8
                elif y > cy:
                    y += 24
                vert_text = font_48.render(str(vert_ids[id]),True,(0,0,0))
                self.screen.blit(vert_text,(x,y-24))
            face_text = font_32.render(chr(ord('A')+face_id), True, (0,0,0))
            self.screen.blit(face_text, (face_x-4,face_y-8))
            
            
        for edge in border_edges:
                x1,y1,z1 = displayed_vertices[edge[0]]
                d = z1 - self.POV[2]
                scalar = D/d # skalar wynikający z tw. Talesa
                X1 = int(cx + x1*scalar)
                Y1 = int(cy - y1*scalar)
                
                x2,y2,z2 = displayed_vertices[edge[1]]
                d = z2 - self.POV[2]
                scalar = D/d # skalar wynikający z tw. Talesa
                X2 = int(cx + x2*scalar)
                Y2 = int(cy - y2*scalar)
                color = (165,42,42)
                pygame.gfxdraw.line(self.screen, X1, Y1, X2, Y2, color)
        pygame.gfxdraw.circle(self.screen, cx, cy, 3, (255,255,0))
        pygame.gfxdraw.aacircle(self.screen, cx, cy, 3, (0,0,0))
        pygame.display.flip()
        #zapisywanie widoku z konturem
        pygame.image.save(self.screen,save_filename+'.jpg')
        try:
            with open(save_filename+'.txt', "w") as file:
                file.write("widoczne ściany: " + str([chr(ord('A')+x) for x in visible_faces]) + '\n')
                file.write("niewidoczne ściany: " + str([chr(ord('A')+x) for x in not_visible_faces]) + '\n')
                file.write("krawędzie konturu widoku: " + str([str(str(self.polyhedron.edges[v][0])+'k'+str(self.polyhedron.edges[v][1])) for v in border_id_edges]) + '\n')
                file.write("ściany wianka nieznikania: " + str([chr(ord('A')+x) for x in border_visible_faces]) + '\n')
                file.write("ściany wianka niepojawiania: " + str([chr(ord('A')+x) for x in border_not_visible_faces]) + '\n')
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            print("unable to save results")
            return
        
        
        #geenerowanie obrazu relacji widoku i obszaru jednowidokowego
        self.screen.fill((250,250,250))
        #rysowanie sfery jednostkowej
        pygame.gfxdraw.aacircle(self.screen, cx, cy, 250, (0,0,0))
        #rysowanie osi współrzędnych z tyłu bryły
        
        ax = ('x+','y+','z+','x-','y-','z-')
        ax_colors = [(255,0,0),(0,0,255),(0,255,0),(255,0,0),(0,0,255),(0,255,0)]
        for i in range(0,6):
            depth = axis[i*2+1][2] - axis[i*2][2]
            if depth >= 0:
                x,y,z = axis[i*2]
                x2,y2,z2 = axis[i*2+1]
                d = z - self.POV[2]
                scalar = D/d # skalar wynikający z tw. Talesa
                XP = int(cx + x*scalar)
                YP = int(cy - y*scalar)
                d2 = z2 - self.POV[2]
                scalar = D/d # skalar wynikający z tw. Talesa
                XK = int(cx + x2*scalar)
                YK = int(cy - y2*scalar)
                pygame.gfxdraw.line(self.screen, XP,YP,XK,YK, ax_colors[i])
                ax_text = font_24.render(ax[i],True, ax_colors[i])
                self.screen.blit(ax_text,(XK,YK-16))
            
        for face_id in visible_faces:
            coords = []
            vert_ids = []
            face_x, face_y = 0,0
            for vert_id in self.polyhedron.faces[face_id]:
                x,y,z = displayed_vertices[vert_id]
                vert_ids.append(vert_id)
                d = z - self.POV[2]
                scalar = D/d # skalar wynikający z tw. Talesa
                X = cx + x*scalar
                Y = cy - y*scalar
                face_x += X
                face_y += Y
                coords.append((X,Y))
            face_x, face_y = face_x/len(self.polyhedron.faces[face_id]), face_y/len(self.polyhedron.faces[face_id])
            coords.append(coords[0])
            vert_ids.append(vert_ids[0])
            pygame.gfxdraw.filled_polygon(self.screen, coords, (127,127,127))
            pygame.gfxdraw.aapolygon(self.screen, coords, (20,20,20))
            pygame.draw.polygon(self.screen, (20,20,20), coords, 1)
        #rysowanie osi współrzędnych przed bryłą
        ax = ('x+','y+','z+','x-','y-','z-')
        ax_colors = [(255,0,0),(0,0,255),(0,255,0),(255,0,0),(0,0,255),(0,255,0)]
        for i in range(0,6):
            depth = axis[i*2+1][2] - axis[i*2][2]
            if depth < 0:
                x,y,z = axis[i*2]
                x2,y2,z2 = axis[i*2+1]
                d = z - self.POV[2]
                scalar = D/d # skalar wynikający z tw. Talesa
                XP = int(cx + x*scalar)
                YP = int(cy - y*scalar)
                d2 = z2 - self.POV[2]
                scalar = D/d # skalar wynikający z tw. Talesa
                XK = int(cx + x2*scalar)
                YK = int(cy - y2*scalar)
                pygame.gfxdraw.line(self.screen, XP,YP,XK,YK, ax_colors[i])
                ax_text = font_24.render(ax[i],True, ax_colors[i])
                self.screen.blit(ax_text,(XK,YK-16))
        
        #ustalanie obszarów 1 widokowych:
        original_view_border = set(border_id_edges)
        border_points = {}
        shift = 0.25
        ox_up_rot, ox_down_rot = 0.0, -shift
        initial_oy_rot = 0.0
        O_PV = (0,0,-1.0)
        left_diffs = []
        right_diffs = []
        while True:
            oy_left_rot, oy_right_rot = initial_oy_rot, initial_oy_rot
            sin_angle_ox = math.sin(math.radians(ox_up_rot))
            cos_angle_ox = math.cos(math.radians(ox_up_rot))
            ox_matrix = [[1.0,    0.0,    0.0],
                         [0.0,    cos_angle_ox,     -sin_angle_ox], 
                         [0.0,    sin_angle_ox,    cos_angle_ox]]
            view_verts_position = [numpy.matmul(vertex, ox_matrix) for vertex in displayed_vertices]
            left_change = None
            right_change = None
            while True:
                sin_angle_oy = math.sin(math.radians(oy_left_rot))
                cos_angle_oy = math.cos(math.radians(oy_left_rot))
                oy_left_matrix = [[cos_angle_oy, 0.0, -sin_angle_oy],
                             [0.0,    1.0,    0.0], 
                             [sin_angle_oy,    0.0,    cos_angle_oy]]
                new_view_verts_position = [numpy.matmul(vertex, oy_left_matrix) for vertex in view_verts_position]
                left_rot_border = set(self.calculate_view_area(new_view_verts_position)[0])
                if left_rot_border.difference(original_view_border) != original_view_border.difference(left_rot_border):
                    break
                oy_left_rot -= shift
                
            view_verts_position = [numpy.matmul(vertex, ox_matrix) for vertex in displayed_vertices]
            while True:
                sin_angle_oy = math.sin(math.radians(oy_right_rot))
                cos_angle_oy = math.cos(math.radians(oy_right_rot))
                oy_right_matrix = [[cos_angle_oy, 0.0, -sin_angle_oy],
                             [0.0,    1.0,    0.0], 
                             [sin_angle_oy,    0.0,    cos_angle_oy]]
                new_view_verts_position = [numpy.matmul(vertex, oy_right_matrix) for vertex in view_verts_position]
                right_rot_border = set(self.calculate_view_area(new_view_verts_position)[0])
                if right_rot_border.difference(original_view_border) != original_view_border.difference(right_rot_border):
                    break
                oy_right_rot += shift
            if oy_right_rot == initial_oy_rot and oy_left_rot == initial_oy_rot:
                break
            right_rotate_matrix = [[math.cos(math.radians(-oy_right_rot)), 0.0, -math.sin(math.radians(-oy_right_rot))],
                             [0.0,    1.0,    0.0], 
                             [math.sin(math.radians(-oy_right_rot)),    0.0,    math.cos(math.radians(-oy_right_rot))]]
            left_rotate_matrix = [[math.cos(math.radians(-oy_left_rot)), 0.0, -math.sin(math.radians(-oy_left_rot))],
                             [0.0,    1.0,    0.0], 
                             [math.sin(math.radians(-oy_left_rot)),    0.0,    math.cos(math.radians(-oy_left_rot))]]
            ox_matrix = [[1.0,    0.0,    0.0],
                         [0.0,    math.cos(math.radians(-ox_up_rot)),     -math.sin(math.radians(-ox_up_rot))], 
                         [0.0,    math.sin(math.radians(-ox_up_rot)),    math.cos(math.radians(-ox_up_rot))]]

            left_border_point = numpy.matmul(O_PV, left_rotate_matrix)
            right_border_point = numpy.matmul(O_PV, right_rotate_matrix)
            left_border_point = numpy.matmul(left_border_point, ox_matrix)
            right_border_point = numpy.matmul(right_border_point, ox_matrix)
            
            d = left_border_point[2] - self.POV[2]
            scalar = D/d # skalar wynikający z tw. Talesa
            X1 = int(cx + left_border_point[0]*scalar)
            Y1 = int(cy - left_border_point[1]*scalar)
            
            d = right_border_point[2] - self.POV[2]
            scalar = D/d # skalar wynikający z tw. Talesa
            X2 = int(cx + right_border_point[0]*scalar)
            Y2 = int(cy - right_border_point[1]*scalar)
            
            border_points[ox_up_rot] = ((X1,Y1), (X2,Y2))
            if not left_change in left_diffs:
                left_diffs.append(left_change)
            if not right_change in right_diffs:
                right_diffs.append(right_change)
            oy_left_rot = (oy_left_rot + oy_right_rot) / 2
            ox_up_rot += shift
            
        initial_oy_rot = 0.0
        while True:
            oy_left_rot, oy_right_rot = initial_oy_rot, initial_oy_rot
            sin_angle_ox = math.sin(math.radians(ox_down_rot))
            cos_angle_ox = math.cos(math.radians(ox_down_rot))
            ox_matrix = [[1.0,    0.0,    0.0],
                         [0.0,    cos_angle_ox,     -sin_angle_ox], 
                         [0.0,    sin_angle_ox,    cos_angle_ox]]
            view_verts_position = [numpy.matmul(vertex, ox_matrix) for vertex in displayed_vertices]
            while True:
                sin_angle_oy = math.sin(math.radians(oy_left_rot))
                cos_angle_oy = math.cos(math.radians(oy_left_rot))
                oy_left_matrix = [[cos_angle_oy, 0.0, -sin_angle_oy],
                             [0.0,    1.0,    0.0], 
                             [sin_angle_oy,    0.0,    cos_angle_oy]]
                new_view_verts_position = [numpy.matmul(vertex, oy_left_matrix) for vertex in view_verts_position]
                left_rot_border = set(self.calculate_view_area(new_view_verts_position)[0])
                if left_rot_border.difference(original_view_border) != original_view_border.difference(left_rot_border):
                    break
                oy_left_rot -= shift
            view_verts_position = [numpy.matmul(vertex, ox_matrix) for vertex in displayed_vertices]
            while True:
                sin_angle_oy = math.sin(math.radians(oy_right_rot))
                cos_angle_oy = math.cos(math.radians(oy_right_rot))
                oy_right_matrix = [[cos_angle_oy, 0.0, -sin_angle_oy],
                             [0.0,    1.0,    0.0], 
                             [sin_angle_oy,    0.0,    cos_angle_oy]]
                new_view_verts_position = [numpy.matmul(vertex, oy_right_matrix) for vertex in view_verts_position]
                right_rot_border = set(self.calculate_view_area(new_view_verts_position)[0])
                if right_rot_border.difference(original_view_border) != original_view_border.difference(right_rot_border):
                    break
                oy_right_rot += shift
            if oy_right_rot == initial_oy_rot and oy_left_rot == initial_oy_rot:
                break
            
            right_rotate_matrix = [[math.cos(math.radians(-oy_right_rot)), 0.0, -math.sin(math.radians(-oy_right_rot))],
                             [0.0,    1.0,    0.0], 
                             [math.sin(math.radians(-oy_right_rot)),    0.0,    math.cos(math.radians(-oy_right_rot))]]
            left_rotate_matrix = [[math.cos(math.radians(-oy_left_rot)), 0.0, -math.sin(math.radians(-oy_left_rot))],
                             [0.0,    1.0,    0.0], 
                             [math.sin(math.radians(-oy_left_rot)),    0.0,    math.cos(math.radians(-oy_left_rot))]]
            ox_matrix = [[1.0,    0.0,    0.0],
                         [0.0,    math.cos(math.radians(-ox_down_rot)),     -math.sin(math.radians(-ox_down_rot))], 
                         [0.0,    math.sin(math.radians(-ox_down_rot)),    math.cos(math.radians(-ox_down_rot))]]

            left_border_point = numpy.matmul(O_PV, left_rotate_matrix)
            right_border_point = numpy.matmul(O_PV, right_rotate_matrix)
            left_border_point = numpy.matmul(left_border_point, ox_matrix)
            right_border_point = numpy.matmul(right_border_point, ox_matrix)
            
            d = left_border_point[2] - self.POV[2]
            scalar = D/d # skalar wynikający z tw. Talesa
            X1 = int(cx + left_border_point[0]*scalar)
            Y1 = int(cy - left_border_point[1]*scalar)
            
            d = right_border_point[2] - self.POV[2]
            scalar = D/d # skalar wynikający z tw. Talesa
            X2 = int(cx + right_border_point[0]*scalar)
            Y2 = int(cy - right_border_point[1]*scalar)
            
            border_points[ox_down_rot] = ((X1,Y1), (X2,Y2))
            if not left_change in left_diffs:
                left_diffs.append(left_change)
            if not right_change in right_diffs:
                right_diffs.append(right_change)
            oy_left_rot = (oy_left_rot + oy_right_rot) / 2
            ox_down_rot -= shift
            
        coords = []
        angle_keys = border_points.keys()
        for key in sorted(angle_keys):
            coords.append(border_points[key][0])
        for key in sorted(angle_keys, reverse=True):
            coords.append(border_points[key][1])
        coords.append(coords[0])
        """
        print()
        print(save_filename)
        print([(chr(ord('A')+id), face_normal_angles[id][1]) for id in range(0,len(face_normal_angles))])
        """
        pygame.draw.polygon(self.screen, (0,0,0), coords, 4)
        pygame.gfxdraw.circle(self.screen, cx, cy, 3, (255,255,0))
        pygame.gfxdraw.aacircle(self.screen, cx, cy, 3, (0,0,0))
        pygame.image.save(self.screen,save_filename+'-O1W.jpg')
        pygame.display.flip()
        
    def calculate_view_area(self, vertices):
        visible_faces = []
        not_visible_faces = []
        face_normals_angles = []
        for face in self.polyhedron.faces:
            #okreslanie widocznosci scian
            verts = [vertices[v] for v in face]
            C = 0,0,0
            for v in verts:
                C = C[0]+v[0], C[1]+v[1], C[2]+v[2]
            C = C[0]/len(verts), C[1]/len(verts), C[2]/len(verts)
            A = verts[0]
            B = verts[1]
            CA = numpy.subtract(A,C)
            CB = numpy.subtract(B,C)
            cross_A = numpy.cross(CA,CB)
            N = [C[i]+cross_A[i] for i in range(0,3)]
            N2 = [C[i]-cross_A[i] for i in range(0,3)]
            S = 0.0, 0.0, 0.0
            CN = numpy.subtract(N,C)
            CS = numpy.subtract(S,C)
            cos_normal = numpy.clip(numpy.dot(CN,CS)/(numpy.linalg.norm(CS)*numpy.linalg.norm(CN)),-1,1)
            angle = math.acos(cos_normal)
            if -90 < math.degrees(angle) < 90:
                normal = N2
            else:
                normal = N
            CN = numpy.subtract(normal,C)
            CS = numpy.subtract(S,C)
            cos_normal = numpy.clip(numpy.dot(CN,CS)/(numpy.linalg.norm(CS)*numpy.linalg.norm(CN)),-1,1)
            angle = math.acos(cos_normal)
            CN = numpy.subtract(normal,C)
            CS = numpy.subtract(self.POV,C)
            cos_normal = numpy.clip(numpy.dot(CN,CS)/(numpy.linalg.norm(CS)*numpy.linalg.norm(CN)),-1,1)
            angle = math.acos(cos_normal)
            face_normals_angles.append((CN, math.degrees(angle)))
            
            if -90 < math.degrees(angle) < 90:
                visible_faces.append(self.polyhedron.faces.index(face))
            else:
                not_visible_faces.append(self.polyhedron.faces.index(face))
        #okreslanie widocznosci krawedzi i konturu widoku
        visible_edges = []
        not_visible_edges = []
        for f in visible_faces:
            face = list(self.polyhedron.faces[f])
            face.append(face[0])
            for i in range(1,len(face)):
                v1 = face[i-1]
                v2 = face[i]
                edge = v1,v2
                if v2 < v1:
                    edge = v2,v1
                if edge not in visible_edges:
                    visible_edges.append(edge)
        for f in not_visible_faces:
            face = list(self.polyhedron.faces[f])
            face.append(face[0])
            for i in range(1,len(face)):
                v1 = face[i-1]
                v2 = face[i]
                edge = v1,v2
                if v2 < v1:
                    edge = v2,v1
                if edge not in not_visible_edges:
                    not_visible_edges.append(edge)
        border_edges = [ x for x in visible_edges if x in not_visible_edges]
        border_visible_faces = []
        border_not_visible_faces = []
        edge_faces_dictionary = {}
        for edge in border_edges:
            edge_faces_dictionary[edge] = []
        for f in visible_faces:
            face = list(self.polyhedron.faces[f])
            face.append(face[0])
            on_edge = False
            for i in range(1,len(face)):
                v1 = face[i-1]
                v2 = face[i]
                edge = v1,v2
                if v2 < v1:
                    edge = v2,v1
                if edge in border_edges:
                    on_edge = True
                    edge_faces_dictionary[edge].append(f)
            if on_edge:
                border_visible_faces.append(f)
        for f in not_visible_faces:
            face = list(self.polyhedron.faces[f])
            face.append(face[0])
            on_edge = False
            for i in range(1,len(face)):
                v1 = face[i-1]
                v2 = face[i]
                edge = v1,v2
                if v2 < v1:
                    edge = v2,v1
                if edge in border_edges:
                    on_edge = True
                    edge_faces_dictionary[edge].append(f)
            if on_edge:
                border_not_visible_faces.append(f)
        border_id_edges = [self.polyhedron.edges.index(x) for x in border_edges]
        return border_id_edges, border_edges, visible_faces, not_visible_faces, border_visible_faces, border_not_visible_faces, face_normals_angles

        
    def main(self):
        if os.path.exists("wyniki"):
            shutil.rmtree("wyniki/", ignore_errors=True)
        os.makedirs("wyniki")
        if not os.path.exists("wyniki"):
            os.makedirs("wyniki")
            
        if not os.path.exists("wyniki/wierzcholki"):
            os.makedirs("wyniki/wierzcholki")
            
        if not os.path.exists("wyniki/krawedzie"):
            os.makedirs("wyniki/krawedzie")
            
        if not os.path.exists("wyniki/sciany"):
            os.makedirs("wyniki/sciany")
        
        print("generowanie widoków wierzchołkowych:",0,"/",self.polyhedron.vert_count, end='\r')
        sys.stdout.flush()
        for i in range(self.polyhedron.vert_count):
            axis, vertices = self.polyhedron.get_centered_on_point(i)
            self.generate(axis, vertices, 'wyniki/wierzcholki/widok'+str(i))
            #sys.stdout.write("\033[F") # Cursor up one line
            print("generowanie widoków wierzchołkowych:",(i+1),"/",self.polyhedron.vert_count, end='\r')
            sys.stdout.flush()
        print()
        print("generowanie widoków krawędziowych:",0,"/",self.polyhedron.edge_count,end='\r')
        sys.stdout.flush()
        for i in range(self.polyhedron.edge_count):
            axis, vertices = self.polyhedron.get_centered_on_edge(i)
            self.generate(axis, vertices, 'wyniki/krawedzie/widok'+str(i))
            #sys.stdout.write("\033[F") # Cursor up one line
            print("generowanie widoków krawędziowych:",(i+1),"/",self.polyhedron.edge_count, end='\r')
            sys.stdout.flush()
        print()
        print("generowanie widoków ściennych:",(0),"/",self.polyhedron.face_count, end='\r')
        sys.stdout.flush()
        for i in range(self.polyhedron.face_count):
            axis, vertices = self.polyhedron.get_centered_on_face(i)
            self.generate(axis, vertices, 'wyniki/sciany/widok'+str(i))
            #sys.stdout.write("\033[F") # Cursor up one line
            print("generowanie widoków ściennych:",(i+1),"/",self.polyhedron.face_count, end='\r')
            sys.stdout.flush()
        print()
        #wyłącz aplikację
        pygame.quit()
        
if __name__ == "__main__":
    vmg = View_model_generator()
    print("done")