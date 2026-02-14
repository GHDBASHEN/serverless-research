const fs = require('fs');
const path = require('path');
const os = require('os');

let isCold = true;

const algorithms = {
  fibonacci: (n) => {
    if (n <= 1) return n;
    return algorithms.fibonacci(n - 1) + algorithms.fibonacci(n - 2);
  },
  matrix_mult: (n) => {
    let size = n;
    let A = new Array(size).fill(0).map(() => new Array(size).fill(Math.random()));
    let B = new Array(size).fill(0).map(() => new Array(size).fill(Math.random()));
    let C = new Array(size).fill(0).map(() => new Array(size).fill(0));

    for (let i = 0; i < size; i++) {
        for (let j = 0; j < size; j++) {
            for (let k = 0; k < size; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
    return C[0][0];
  },
  prime_sieve: (n) => {
    let size = n;
    if (size < 2) return 0;
    let primes = new Uint8Array(size + 1).fill(1);
    primes[0] = 0;
    primes[1] = 0;
    for (let i = 2; i * i <= size; i++) {
        if (primes[i]) {
            for (let j = i * i; j <= size; j += i) {
                primes[j] = 0;
            }
        }
    }
    let count = 0;
    for (let i = 2; i <= size; i++) if (primes[i]) count++;
    return count;
  },
  file_io: (n) => {
    // n is size in bytes
    const filename = path.join(os.tmpdir(), `test_${Math.floor(Math.random() * 1000000)}.txt`);
    try {
        const buffer = Buffer.alloc(n, 'x');
        fs.writeFileSync(filename, buffer);
        const data = fs.readFileSync(filename);
        return data.length;
    } finally {
        if (fs.existsSync(filename)) {
            fs.unlinkSync(filename);
        }
    }
  },
  float_ops: (n) => {
    let val = 1.0;
    for (let i = 0; i < n; i++) {
        val = Math.sin(val) * Math.cos(val) + Math.tan(val);
    }
    return val;
  }
};

const handle = async (event) => {
    const startTime = process.hrtime();
    
    // Parse Payload
    let payload = event;
    if (event.body) {
        if (typeof event.body === 'string') {
            try { payload = JSON.parse(event.body); } catch(e) {}
        } else {
            payload = event.body;
        }
    }
    
    const workload = payload.workload || 'float_ops';
    const size = parseInt(payload.size || 1000);
    
    let result = null;
    if (algorithms[workload]) {
        result = algorithms[workload](size);
    }

    const diff = process.hrtime(startTime);
    const durationMs = (diff[0] * 1000) + (diff[1] / 1e6);
    
    const memoryUsage = process.memoryUsage();
    const memoryMb = memoryUsage.rss / 1024 / 1024;
    
    const response = {
        duration_ms: durationMs,
        memory_mb: memoryMb,
        cold_start: isCold
    };
    
    isCold = false;
    return response;
};

// AWS Lambda
exports.handler = async (event) => {
    return await handle(event);
};

// Azure Functions
module.exports = async function (context, req) {
    const res = await handle(req.body || req.query);
    context.res = {
        body: res
    };
};

// Google Cloud Functions
exports.googleHandler = async (req, res) => {
    const result = await handle(req.body || req.query);
    res.status(200).send(result);
};
