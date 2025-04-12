const http = require('http');

const API_URL = 'http://localhost:5000';
const options = {
  hostname: 'localhost',
  port: 5000,
  path: '/generate_recipe',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  }
};

const requestBody = JSON.stringify({
  ingredients: ['chicken'],
  preferences: { style: '', category: '', language: 'english', isRandom: false }
});

async function testApi() {
  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        if (res.statusCode !== 200) {
          reject(new Error('API farted: ' + res.statusCode));
        } else {
          console.log('Response:', JSON.parse(data));
          resolve();
        }
      });
    });

    req.on('error', (error) => {
      console.error('Error:', error);
      reject(error);
    });

    req.write(requestBody);
    req.end();
  });
}

testApi().catch(error => console.error('Promise error:', error));