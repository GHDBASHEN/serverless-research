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
  },
  cpu_math_1: (n) => {
    let val = 0; for(let i=0; i<n*1000; i++) val += Math.sin(i); return val;
  },
  cpu_math_2: (n) => {
    let val = 1; for(let i=0; i<n*100; i++) val = Math.pow(val * 1.0001, 1.01); return val;
  },
  cpu_math_3: (n) => {
    let val = 0; for(let i=0; i<n*500; i++) { let f=1; for(let j=1; j<=(i%50); j++) f*=j; val+=f; } return val;
  },
  cpu_math_4: (n) => {
    let val = 0; for(let i=0; i<n*1000; i++) val += Math.sqrt(i); return val;
  },
  cpu_math_5: (n) => {
    let val = 0; let v1 = new Array(n*100); let v2 = new Array(n*100); for(let i=0; i<n*100; i++) { v1[i]=Math.random(); v2[i]=Math.random(); val+=v1[i]*v2[i]; } return val;
  },
  mem_alloc_1: (n) => {
    let arr = new Array(n*10000); for(let i=0; i<arr.length; i++) arr[i]=i; return arr.length;
  },
  mem_alloc_2: (n) => {
    let obj = {}; for(let i=0; i<n*5000; i++) obj[i] = i; return Object.keys(obj).length;
  },
  mem_alloc_3: (n) => {
    let arr = new Array(n*2000).fill(0).map((_,i) => new Array(10).fill(i)); return arr.length;
  },
  mem_string_4: (n) => {
    let s = 'x'.repeat(n*10000); return s.length;
  },
  mem_dict_5: (n) => {
    let d = {}; for(let i=0; i<n*1000; i++) d['key_'+i] = {nested: i}; return Object.keys(d).length;
  },
  disk_io_1: (n) => {
    let fs = require('fs'); let f='/tmp/d1_'+Math.random()+'.txt'; fs.writeFileSync(f, 'A'.repeat(n*1000)); fs.unlinkSync(f); return 1;
  },
  disk_io_2: (n) => {
    let fs = require('fs'); let f='/tmp/d2_'+Math.random()+'.txt'; fs.writeFileSync(f, 'B'.repeat(n*2000)); fs.unlinkSync(f); return 1;
  },
  disk_io_3: (n) => {
    let fs = require('fs'); let crypto = require('crypto'); let f='/tmp/d3_'+Math.random()+'.txt'; fs.writeFileSync(f, crypto.randomBytes(n*500)); fs.unlinkSync(f); return 1;
  },
  disk_io_4: (n) => {
    let fs = require('fs'); let f='/tmp/d4_'+Math.random()+'.txt'; let d=''; for(let i=0; i<n*100; i++) d+=i; fs.writeFileSync(f, d); fs.unlinkSync(f); return 1;
  },
  disk_io_5: (n) => {
    let fs = require('fs'); let f='/tmp/d5_'+Math.random()+'.txt'; fs.writeFileSync(f, 'X'.repeat(n*100)); fs.readFileSync(f); fs.unlinkSync(f); return 1;
  },
  net_sim_1: async (n) => {
    return new Promise(r => setTimeout(r, Math.min(n*1, 2000)));
  },
  net_sim_2: async (n) => {
    return new Promise(r => setTimeout(r, Math.min(n*2, 2000)));
  },
  net_sim_3: async (n) => {
    return new Promise(r => setTimeout(r, Math.min(n*3, 2000)));
  },
  net_sim_4: async (n) => {
    return new Promise(r => setTimeout(r, Math.min(n*4, 2000)));
  },
  net_sim_5: async (n) => {
    return new Promise(r => setTimeout(r, Math.min(n*5, 2000)));
  },
  data_proc_1: (n) => {
    let a = []; for(let i=0; i<n*100; i++) a.push(i); let d = a.join(','); return d.split(',').length;
  },
  data_proc_2: (n) => {
    let a = []; for(let i=0; i<n*100; i++) a.push({id: i}); let j = JSON.stringify(a); return JSON.parse(j).length;
  },
  data_proc_3: (n) => {
    let crypto = require('crypto'); let b = crypto.randomBytes(n*100).toString('base64'); return Buffer.from(b, 'base64').length;
  },
  data_proc_4: (n) => {
    let val = 0; for(let i=0; i<n*1000; i++) { if(i%2===0 && i%3===0) val++; } return val;
  },
  data_proc_5: (n) => {
    let s = 'abc 123 '.repeat(n*100); let m = s.match(/\d+/g); return m ? m.length : 0;
  },
  crypto_1: (n) => {
    let crypto = require('crypto'); for(let i=0; i<n*100; i++) crypto.createHash('md5').update(String(i)).digest('hex'); return 1;
  },
  crypto_2: (n) => {
    let crypto = require('crypto'); for(let i=0; i<n*100; i++) crypto.createHash('sha1').update(String(i)).digest('hex'); return 1;
  },
  crypto_3: (n) => {
    let crypto = require('crypto'); for(let i=0; i<n*100; i++) crypto.createHash('sha256').update(String(i)).digest('hex'); return 1;
  },
  crypto_4: (n) => {
    let crypto = require('crypto'); for(let i=0; i<n*100; i++) crypto.createHash('sha512').update(String(i)).digest('hex'); return 1;
  },
  crypto_5: (n) => {
    let crypto = require('crypto'); crypto.pbkdf2Sync('pass', 'salt', n*100, 64, 'sha256'); return 1;
  },
  web_biz_1: (n) => {
    let val=0; for(let i=0; i<n*10; i++) val += (Math.random()*100) * (Math.floor(Math.random()*5)+1); return val;
  },
  web_biz_2: (n) => {
    let val=0; for(let i=0; i<n*100; i++) { if(Math.random()>0.5) val++; } return val;
  },
  web_biz_3: (n) => {
    let h = '<h1>Header</h1>'.repeat(n*10); return h.replace(/h1>/g, 'h2>').length;
  },
  web_biz_4: (n) => {
    let s=''; let chars='abcdef'; for(let i=0; i<n*100; i++) s+=chars[Math.floor(Math.random()*chars.length)]; return s.length;
  },
  web_biz_5: (n) => {
    let a=[]; for(let i=0; i<n*100; i++) a.push(Math.floor(Math.random()*100)); a.sort((x,y)=>x-y); return a.length;
  },
  sci_1: (n) => {
    let d=[]; let sum=0; for(let i=0; i<n*100; i++) { let v=Math.random(); d.push(v); sum+=v; } let mean=sum/d.length; let val=0; for(let v of d) val += Math.pow(v-mean,2); return val;
  },
  sci_2: (n) => {
    let sum=0; for(let i=0; i<n*100; i++) sum += i + (i*2 + Math.random()); return sum;
  },
  sci_3: (n) => {
    let d=[]; let max=0; for(let i=0; i<n*100; i++) { let v=Math.random(); d.push(v); if(v>max) max=v; } d = d.map(v=>v/max); return d.length;
  },
  sci_4: (n) => {
    let in_c=0; let t=n*100; for(let i=0; i<t; i++) { if(Math.pow(Math.random(),2)+Math.pow(Math.random(),2)<=1) in_c++; } return in_c*4/t;
  },
  sci_5: (n) => {
    let val=0; for(let i=1; i<n*100; i++) val+=Math.log(i); return val;
  },

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
        result = await algorithms[workload](size);
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
exports.main = async function (context, req) {
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
