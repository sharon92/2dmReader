#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <chrono>
#include <stdio.h>
using namespace std::chrono;

struct E3T {
    uint32_t id, Node1, Node2, Node3, MaterialID;    
};

struct E4Q {
    uint32_t id, Node1, Node2, Node3, Node4, MaterialID;    
};

struct Coords {
    uint32_t id, MaterialID;    
    double X,Y;
    float Z;
};

struct Mesh {
    std::vector<E3T> triangles;
    std::vector<E4Q> patches;
    std::vector<Coords> pos;
};

struct MeshVector {
    std::vector<std::vector<uint32_t>> triangles;
    std::vector<std::vector<uint32_t>> patches;
    std::vector<Coords> pos;
};

int main(int argc, char** argv)
{
    // Get starting timepoint
    auto start = high_resolution_clock::now();

    if (argc == 1) {
        std::cout << "Path to Mesh Data not provided!";
        return 1;
    }
    
    std::ifstream mesh_path{argv[1]};
  
    if (!mesh_path) {
        std::cout << "Couldn't open Mesh file!";
        return 1;
    }

    Mesh mesh;
    mesh.triangles.reserve(20000000);
    mesh.pos.reserve(10000000);
    std::string card{};
    std::string line{};
    E3T triangle_i;
    E4Q patch_i;
    Coords pos_i;

    while (!mesh_path.eof()){
        std::getline(mesh_path,line);
        if (line.substr(0,4) == "E3T "){
            std::stringstream ss{line.substr(4)};
            ss >> triangle_i.id >> triangle_i.Node1 >> triangle_i.Node2 >> triangle_i.Node3 >> triangle_i.MaterialID;
            mesh.triangles.push_back(triangle_i);
        } else if (line.substr(0,4) == "E4Q ") {
            std::stringstream ss{line.substr(4)};
            ss >> patch_i.id >> patch_i.Node1 >> patch_i.Node2 >> patch_i.Node3 >> patch_i.Node4 >> patch_i.MaterialID;
            mesh.patches.push_back(patch_i);
        } else if (line.substr(0,3) == "ND ") {
            std::stringstream ss{line.substr(3)};
            mesh_path >> pos_i.id >> pos_i.X >> pos_i.Y >> pos_i.Z ;
            mesh.pos.push_back(pos_i);
        }

        // mesh_path >> card;
        // if (card == "E3T"){
        //     mesh_path >> triangle_i.id >> triangle_i.Node1 >> triangle_i.Node2 >> triangle_i.Node3 >> triangle_i.MaterialID;
        //     mesh.triangles.push_back(triangle_i);
        // } else if (card == "E4Q") {
        //     mesh_path >> patch_i.id >> patch_i.Node1 >> patch_i.Node2 >> patch_i.Node3 >> patch_i.Node4 >> patch_i.MaterialID;
        //     mesh.patches.push_back(patch_i);
        // } else if (card == "ND") {
        //     mesh_path >> pos_i.id >> pos_i.X >> pos_i.Y >> pos_i.Z ;
        //     mesh.pos.push_back(pos_i);
        // }
        // std::getline(mesh_path,line);
        // std::cout << "Card: " << card << std:: endl;
        // std::cout << "Values: " << line << std:: endl;
        // std::stringstream ss{line};
        // if (card == "E3T"){
        //     ss >> triangle_i.id >> triangle_i.Node1 >> triangle_i.Node2 >> triangle_i.Node3 >> triangle_i.MaterialID;
        //     mesh.triangles.push_back(triangle_i);
        // } else if (card == "E4Q") {
        //     ss >> patch_i.id >> patch_i.Node1 >> patch_i.Node2 >> patch_i.Node3 >> patch_i.Node4 >> patch_i.MaterialID;
        //     mesh.patches.push_back(patch_i);
        // } else if (card == "ND") {
        //     ss >> pos_i.id >> pos_i.X >> pos_i.Y >> pos_i.Z ;
        //     mesh.pos.push_back(pos_i);
        // }
    }
    mesh_path.close();
    
    std::cout << "The Input mesh has \n\t" << mesh.triangles.size() << " triangles\n\t"
    << mesh.patches.size() << " patches\n\t" << mesh.pos.size() << " Nodes\n";

    // Get ending timepoint
    auto stop = high_resolution_clock::now();
    auto duration = duration_cast<seconds>(stop - start);
 
    std::cout << "Time taken: " << duration.count() << " seconds" << std::endl;
    return 0;
}