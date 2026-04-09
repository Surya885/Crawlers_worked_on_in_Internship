class PriorityQueue {
  constructor() {
    this.heap = [];
  }

  get size() {
    return this.heap.length;
  }

  push(item) {
    this.heap.push(item);
    this.#bubbleUp(this.heap.length - 1);
  }

  pop() {
    if (!this.heap.length) return null;
    const top = this.heap[0];
    const last = this.heap.pop();
    if (this.heap.length) {
      this.heap[0] = last;
      this.#bubbleDown(0);
    }
    return top;
  }

  #bubbleUp(index) {
    while (index > 0) {
      const parent = Math.floor((index - 1) / 2);
      if (this.heap[parent].score >= this.heap[index].score) break;
      [this.heap[parent], this.heap[index]] = [this.heap[index], this.heap[parent]];
      index = parent;
    }
  }

  #bubbleDown(index) {
    const n = this.heap.length;
    while (true) {
      let largest = index;
      const left = index * 2 + 1;
      const right = index * 2 + 2;
      if (left < n && this.heap[left].score > this.heap[largest].score) largest = left;
      if (right < n && this.heap[right].score > this.heap[largest].score) largest = right;
      if (largest === index) break;
      [this.heap[largest], this.heap[index]] = [this.heap[index], this.heap[largest]];
      index = largest;
    }
  }
}

module.exports = PriorityQueue;
