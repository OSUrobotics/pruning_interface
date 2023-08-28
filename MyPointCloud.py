#!/usr/bin/env python3

import pymesh
import numpy as np
from ReadWrite import ReadWrite

#########################################################################################
# NAME: MyPointCloud
# DESCRIPTION: Used to read in the pointclouds for the tree
#   - taken from OSURobotics/treefitting repository with file of the same name
# This class is a child of the ReadWrite class
#########################################################################################

class MyPointCloud(ReadWrite):
    def __init__(self):
        super(MyPointCloud, self).__init__("MYPOINTCLOUD")
        self.offsets = []

        # loop backwards from 2 to set the offsets for the function
        for ix in range(-1, 2):
            for iy in range(-1, 2):
                for iz in range(-1, 2):
                    self.offsets.append([ix, iy, iz])

        # load in point cloud information
        self.pcd_data = None # meant for storing the vertices
        self.pcd_data_name = ""
        self.min_pt = [1e30, 1e30, 1e30] # set to arbitrarily large so all values will be smaller
        self.max_pt = [-1e30, -1e30, -1e30]


        # creating the bins
        self.div = 0.005                 # width of the bins
        self.start_xyz = [0.0, 0.0, 0.0] # bottom left corner of box containing points
        self.n_bins_xyz = [1, 1, 1]      # number of bins in each direction
        self.bin_offset = [1, 1, 1]      # for mapping bin xi, yi, zi to unique numbers

        # mapping bin xi, yi, zi to single indices
        self.bin_ids = []  # bin index for each point, can recover ix, iy, iz from _bin_ipt
        self.bin_list = {} # dictionary of bins with bin index as key and value is list of points in bin

    ##################################################################
    # NAME: pts
    # INPUTS: None
    # OUTPUTS: the list of points stored as vertices in self.pcd_data
    # DESCRIPTION: Returns the list of points
    ##################################################################
    def pts(self):
        return self.pcd_data.vertices


    ##################################################################
    # NAME: point
    # INPUTS: 
    #   - i: an integer representing the index of a specific point
    # OUTPUTS: the point stored at that specific index
    # DESCRIPTION: Returns the point for a specific index
    ##################################################################
    def point(self, i):
        return self.pcd_data.vertices[i]
    

    ##################################################################
    # NAME: num_pts
    # INPUTS: None
    # OUTPUTS: an integer representing the length of points
    # DESCRIPTION: Returns the number of points currently stored as
    #              vertices under self.pcd_data
    ##################################################################
    def num_pts(self):
        return len(self.pcd_data.vertices)
    
    ##################################################################
    # NAME: bin_index_pt
    # INPUTS: 
    #   - p: a 1x3 array representing a 3D point
    # OUTPUTS: 
    #   - pt_index: a 1x3 array representing the index of the pt from bin size
    # DESCRIPTION: Calculates the index of the pt passed in
    ##################################################################
    def bin_index_pt(self, p):
        pt_index = [0, 0, 0] # the index of the point
        for i in range(0, 3):
            fx = (p[i] - self.start_xyz[i]) / self.div
            pt_index[i] = int(np.floor(fx))
        
        return pt_index
    
    ##################################################################
    # NAME: bin_index_map
    # INPUTS: 
    #   - ipt: 1x3 array of index points xi, yi, zi
    # OUTPUTS: a single index value that maps the bin index to the index 
    # DESCRIPTION: Maps the bin index into a single index value
    ##################################################################
    def bin_index_map(self, ipt):
        return ipt[2] + ipt[1] * self.bin_offset[0] + ipt[0] *self.bin_offset[1]


    ##################################################################
    # NAME: bin_ipt
    # INPUTS: 
    #   - index: an integer representing the bin index
    # OUTPUTS: point index as an array [xi, yi, zi]
    # DESCRIPTION: Returns the x, y, z point in real space that is the bin center
    ##################################################################
    def bin_ipt(self, index):
        zi = index % self.n_bins_xyz[2]
        xy_index = int((index - zi) / self.n_bins_xyz[2])

        yi = xy_index % self.n_bins_xyz[1]
        x_index = xy_index = yi

        xi = int(x_index / self.n_bins_xyz[1])
        return [xi, yi, zi]
    

    ##################################################################
    # NAME: bin_center
    # INPUTS: 
    #   - index: an integer representing the bin index
    # OUTPUTS: a 1x3 array of the point in real space
    # DESCRIPTION: calculates and returns the real space point that is centered in the bin
    ##################################################################
    def bin_center(self, index):
        ipt = self.bin_ipt(index)

        pt = []
        for i in range(0, 3):
            pt.append(self.start_xyz[i] + (ipt[i] + 0.5) * self.div)
        
        return np.array(pt)
    

    @staticmethod
    def dist(p, q):
        v = [(q[i] - p[i]) * (q[i] - p[i]) for i in range(0, 3)]
        return np.sqrt(sum(v))

    @staticmethod
    def dist_norm(p, q, pn, qn):
        dist_pt = MyPointCloud.dist(p, q)
        norm_align = np.dot(pn, qn)
        if norm_align < 0:
            return 2
        return dist_pt + 1 - norm_align

    
    ##################################################################
    # NAME: bin_center
    # INPUTS: 
    #   - pi_index: index of point
    #   - radius_search: maximum radius to try 
    # OUTPUTS: a list of ids of a neighbor bins within radius_search
    # DESCRIPTION: Searches and finds points within a given radius from the initial point index
    ##################################################################
    def find_neighbor_bins(self, pi_index, radius_search):
        """
        Search the neighboring bins for points within the given radius
        :param: pi_index: index of point
        :param: radius_search: maximum radius to try
        :return: list of ids of neighbor bin ids within radius_search
        """
        p = self.point(pi_index)
        last_count = 0
        ret_list = [self.bin_ids[pi_index]]
        visited = {self.bin_ids[pi_index]: 0.0}
        while len(ret_list) > last_count:
            ipt = self.bin_ipt(ret_list[last_count])
            for o in self.offsets:
                ipt_search = [ipt[i] + o[i] for i in range(0, 3)]
                i_bin = self.bin_index_map(ipt_search)
                if i_bin in self.bin_list and i_bin not in visited:
                    q = self.bin_center(i_bin)
                    dist_to_bin = self.dist(p, q)
                    visited[i_bin] = dist_to_bin
                    if dist_to_bin < radius_search:
                        ret_list.append(i_bin)
            last_count += 1
        return ret_list


    def find_connected(self, pi_start, in_radius=0.05):
        """
        Find all the points that are within the radius AND connected (breadth first search)
        :param pi_start: Point index to start at
        :param in_radius: Maximum Euclidean distance allowed
        :return: Dictionary of neighbors containing distances to neighbors (id, pt, dist)
        """
        bin_id_list = self.find_neighbor_bins(pi_start, in_radius + self.div)
        p = self.pt(pi_start)
        ret_list = []
        for i_bin in bin_id_list:
            for q_id in self.bin_list[i_bin]:
                q = self.pt(q_id)
                d_pq = self.dist(p, q)
                if d_pq < in_radius:
                    ret_list.append((q_id, q, d_pq))
        return ret_list

    def reorder_pts_in_bins(self):
        """
        Put the point that is closest to the center of the bin first in the list
        :return: None
        """
        for k, bl in self.bin_list.items():
            pt_center = self.bin_center(k)
            dist_to_center = []
            for p_id in bl:
                dist_to_center.append((p_id, MyPointCloud.dist(pt_center, self.pt(p_id))))
            dist_to_center.sort(key=lambda list_item: list_item[1])

            for i in range(0, len(bl)):
                bl[i] = dist_to_center[i][0]


    def smallest_branch_width(self):
        return 3.0 * self.div

    
    def create_bins(self, in_smallest_branch_width=0.01):
        """
        Make bins and put points in the bins. Aim for bins that are 1/3 radius of smallest branch width
        :param in_smallest_branch_width: Smallest branch width
        :return: bin list
        """
        max_width = 0
        for i in range(0, 3):
            max_width = max(max_width, self.max_pt[i] - self.min_pt[i])
        self.div = in_smallest_branch_width / 3.0
        # pad by one row of bins
        self.start_xyz = [self.min_pt[i] - self.div - 0.0001 for i in range(0, 3)]
        self.n_bins_xyz = [int(np.ceil((self.max_pt[i] + self.div - self.start_xyz[i]) / self.div)) for i in range(0, 3)]
        # For mapping bin xi,yi,zi to single indes
        self.bin_offset = [self.n_bins_xyz[2], self.n_bins_xyz[2] * self.n_bins_xyz[1]]

        # Put each point in its bin
        self.bin_ids = []
        self.bin_list = {}
        min_ipt = [1000, 1000, 1000]
        max_ipt = [0, 0, 0]

        print("Finding bins n points: {0}, div {1:0.4f}".format(self.num_pts(), self.div))
        for i, p in enumerate(self.pts()):
            if i % 1000 == 0:
                if i % 10000 == 0:
                    print("{0} ".format(i), end='')

            ipt = self.bin_index_pt(p)
            for j in range(0, 3):
                min_ipt[j] = min(min_ipt[j], ipt[j])
                max_ipt[j] = max(max_ipt[j], ipt[j])
            index = self.bin_index_map(ipt)
            self.bin_ids.append(index)
            try:
                list_in_bin = self.bin_list[index]
                list_in_bin.append(i)
                self.bin_list[index] = list_in_bin
            except KeyError:
                self.bin_list[index] = [i]

        # Stats on bin occupancy
        n_pts_in_bin_avg = 0
        n_count = 0
        max_count = 0

        # bins_as_bit_arrays = {}
        for k, pts_in_bin in self.bin_list.items():
            n_count += 1
            n_pts_in_bin_avg += len(pts_in_bin)
            max_count = max(max_count, len(pts_in_bin))

            """
            #  bin_bit_array = len(my_pcd.pc_data) * bitarray('0')
            bin_bit_array = []
            for i in pts_in_bin:
                bin_bit_array.append(i)
                
            #  bins_as_bit_arrays[k] = bin_bit_array
            """

        for i in range(0, 3):
            if min_ipt[i] == 0 or max_ipt[i] > self.n_bins_xyz[i] - 1:
                raise ValueError("No padding")

        self.reorder_pts_in_bins()
        print("Count {0} avg {1} total {2} max {3}".format(n_count, n_pts_in_bin_avg / n_count, len(self.bin_ids), max_count))

        return self.bin_list

    def load_point_cloud(self, file_name=None):
        if file_name is None:
            file_name = self.pcd_data_name
        else:
            self.pcd_data_name = file_name
        self.pcd_data = pymesh.load_mesh(file_name)
        """
        self.pc_data = []
        
        for p in pcd_data.vertices:
            if p[1] > 1.25 or p[2] > 1.7:
                continue
            self.pc_data.append(p)

        self.pc_data = np.array(self.pc_data)
        """

        #  Find bounding box
        self.min_pt = [1e30, 1e30, 1e30]
        self.max_pt = [-1e30, -1e30, -1e30]
        for p in self.pts():
            for i in range(0, 3):
                self.min_pt[i] = min(self.min_pt[i], p[i])
                self.max_pt[i] = max(self.max_pt[i], p[i])

    def read(self, fid):
        self.check_header(fid)
        self.read_class_members(fid)
        self.pcd_data = pymesh.load_mesh(self.pcd_data_name)

    def write(self, fid):
        self.write_header(fid)
        self.write_class_members(fid, dir(self), MyPointCloud, ["pcd_data"])
        self.write_footer(fid)