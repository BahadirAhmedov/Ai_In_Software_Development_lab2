package main

import (
	"fmt"
	"sort"
	"strconv"
	"strings"
	"sync"
)

const multiHashThreads = 6

// ExecutePipeline соединяет воркеры каналами: out воркера i становится in воркера i+1.
// Каждый out закрывается после завершения своего воркера, чтобы следующий вышел из range.
func ExecutePipeline(jobs ...job) {
	wg := &sync.WaitGroup{}
	in := make(chan interface{})
	close(in)

	for _, j := range jobs {
		out := make(chan interface{}, MaxInputDataLen)
		wg.Add(1)
		go func(j job, in, out chan interface{}) {
			defer wg.Done()
			defer close(out)
			j(in, out)
		}(j, in, out)
		in = out
	}

	wg.Wait()
}

// SingleHash считает crc32(data)+"~"+crc32(md5(data)).
// md5 вызывается строго по одному (иначе перегрев), crc32 - параллельно.
func SingleHash(in, out chan interface{}) {
	wg := &sync.WaitGroup{}
	md5Mu := &sync.Mutex{}

	for dataRaw := range in {
		data := fmt.Sprint(dataRaw)
		wg.Add(1)
		go func(data string) {
			defer wg.Done()

			crcData := make(chan string, 1)
			go func() {
				crcData <- DataSignerCrc32(data)
			}()

			md5Mu.Lock()
			md5 := DataSignerMd5(data)
			md5Mu.Unlock()

			crcMd5 := DataSignerCrc32(md5)
			out <- <-crcData + "~" + crcMd5
		}(data)
	}

	wg.Wait()
}

// MultiHash считает crc32(th+data) для th=0..5 и склеивает результаты в порядке th.
func MultiHash(in, out chan interface{}) {
	wg := &sync.WaitGroup{}

	for dataRaw := range in {
		data := fmt.Sprint(dataRaw)
		wg.Add(1)
		go func(data string) {
			defer wg.Done()

			var hashes [multiHashThreads]string
			thWg := &sync.WaitGroup{}
			for th := 0; th < multiHashThreads; th++ {
				thWg.Add(1)
				go func(th int) {
					defer thWg.Done()
					hashes[th] = DataSignerCrc32(strconv.Itoa(th) + data)
				}(th)
			}
			thWg.Wait()

			out <- strings.Join(hashes[:], "")
		}(data)
	}

	wg.Wait()
}

// CombineResults собирает все результаты, сортирует и склеивает через "_".
func CombineResults(in, out chan interface{}) {
	var results []string
	for dataRaw := range in {
		results = append(results, fmt.Sprint(dataRaw))
	}
	sort.Strings(results)
	out <- strings.Join(results, "_")
}
