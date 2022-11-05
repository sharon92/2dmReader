#include <iostream>
#include <string>
#include <cstring>
#include <vector>
#include <chrono>
#include <stdio.h>
#include <memory>
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

int main(int argc, char** argv)
{
    // Get starting timepoint
    auto start = std::chrono::high_resolution_clock::now();

    if (argc == 1) {
        std::cout << "Path to Mesh Data not provided!";
        return 1;
    }

    FILE * mesh_path;
    mesh_path = fopen(argv[1], "r");
  
    if (mesh_path == NULL) {
        std::cout << "Couldn't open Mesh file!";
        return 1;
    }

    
    std::vector<uint32_t> Nodes;
    
    int match{0};

    for (int i{0}; i < 10; ++i) {
        
        char card[]{};
        uint32_t id{0},n1{0},n2{0},n3{0},m{0};
        match = fscanf(mesh_path,"E3T %u %u %u %u %u\n",  &id, &n1, &n2, &n3, &m);
        
        if ( match == 5) {
                std::cout << id << ": " << n1 << ", " << n2 << ", " << n3 << std::endl;
                Nodes.push_back(id);

            } 

        fgets(card,9999,mesh_path);
        std::cout << card;
    }

    // while (!feof(mesh_path)){
    //     if (strcmp(fgets(card,5,mesh_path), "E3T ") == 0) {
    //         fscanf(mesh_path,"%u %u %u %u %u \n",
    //         &triangle_i.id, &triangle_i.Node1, &triangle_i.Node2, &triangle_i.Node3, &triangle_i.MaterialID);

    //     }
    //     else {
    //         fgets(card,99999,mesh_path);
    //     }

            
    // }
    fclose (mesh_path);
    
    // std::cout << "The Input mesh has \n\t" << mesh->triangles.size() << " triangles\n\t"
    // << mesh->patches.size() << " patches\n\t" << mesh->pos.size() << " Nodes\n";

    // Get ending timepoint
    auto stop = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::seconds>(stop - start);
 
    std::cout << "Time taken: " << duration.count() << " seconds" << std::endl;
    return 0;
}