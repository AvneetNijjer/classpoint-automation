
# Additional NPM Scripts

Add these scripts to your package.json for easier management:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "start:backend": "python automation_backend.py",
    "start:full": "concurrently \"npm run dev\" \"python automation_backend.py\"",
    "install:python": "pip install -r requirements.txt"
  }
}
```

To install concurrently for running both servers:
```bash
npm install --save-dev concurrently
```

Then you can run both frontend and backend with:
```bash
npm run start:full
```
