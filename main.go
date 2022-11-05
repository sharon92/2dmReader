package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"
)

type E3T struct {
	id         []uint32
	node1      []uint32
	node2      []uint32
	node3      []uint32
	materialId []uint16
}

type E4Q struct {
	id         []uint32
	node1      []uint32
	node2      []uint32
	node3      []uint32
	node4      []uint32
	materialId []uint16
}

type Elements struct {
	E3T
	E4Q
}

type Nodes struct {
	id []uint32
	x  []float64
	y  []float64
	z  []float32
}

func main() {
	start := time.Now()
	// path := "C:/Projects/test/hydro_as-2d.2dm"
	// path := "C:/Projects/starkregen/hydro_as-2d.2dm"
	path := os.Args[1]
	file, _ := os.Open(path)
	defer file.Close()

	scanner := bufio.NewScanner(file)

	elements := Elements{}
	nodes := Nodes{}
	for scanner.Scan() {
		if scanner.Text()[:4] == "E3T " || scanner.Text()[:4] == "E4Q " {
			elements.Update(scanner.Text())
		}
		if scanner.Text()[:3] == "ND " {
			nodes.Update(scanner.Text())
		}

	}
	fmt.Println(len(elements.E3T.materialId))
	fmt.Println(len(elements.E4Q.materialId))
	fmt.Println(len(nodes.id))
	fmt.Println(time.Since(start))
	fmt.Println(nodes.z[:10])

}

func (e *Elements) Update(s string) {
	l := strings.Fields(s)
	a1, _ := strconv.Atoi(l[1])
	a2, _ := strconv.Atoi(l[2])
	a3, _ := strconv.Atoi(l[3])
	a4, _ := strconv.Atoi(l[4])
	if s[:4] == "E3T " {
		(*e).E3T.id = append((*e).E3T.id, uint32(a1))
		(*e).E3T.node1 = append((*e).E3T.node1, uint32(a2))
		(*e).E3T.node2 = append((*e).E3T.node2, uint32(a3))
		(*e).E3T.node3 = append((*e).E3T.node3, uint32(a4))
		a5, _ := strconv.Atoi(l[5])
		(*e).E3T.materialId = append((*e).E3T.materialId, uint16(a5))

	}
	if s[:4] == "E4Q " {
		(*e).E4Q.id = append((*e).E4Q.id, uint32(a1))
		(*e).E4Q.node1 = append((*e).E4Q.node1, uint32(a2))
		(*e).E4Q.node2 = append((*e).E4Q.node2, uint32(a3))
		(*e).E4Q.node3 = append((*e).E4Q.node3, uint32(a4))
		a5, _ := strconv.Atoi(l[5])
		(*e).E4Q.node4 = append((*e).E4Q.node4, uint32(a5))
		a6, _ := strconv.Atoi(l[6])
		(*e).E4Q.materialId = append((*e).E4Q.materialId, uint16(a6))
	}

}

func (n *Nodes) Update(s string) {
	l := strings.Fields(s)
	a1, _ := strconv.Atoi(l[1])
	a2, _ := strconv.ParseFloat(l[2], 64)
	a3, _ := strconv.ParseFloat(l[3], 64)
	a4, _ := strconv.ParseFloat(l[4], 32)
	(*n).id = append((*n).id, uint32(a1))
	(*n).x = append((*n).x, a2)
	(*n).y = append((*n).y, a3)
	(*n).z = append((*n).z, float32(a4))
}
