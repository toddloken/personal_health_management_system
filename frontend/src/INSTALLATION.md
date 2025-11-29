# PythonPHMS Frontend - Installation Instructions

## Quick Start for Windows

You need to copy all files from the `frontend` folder to your project directory:
`C:\Users\rocca\PycharmProjects\PythonPHMS\frontend`

## Manual Installation Steps

1. **Download the frontend folder** from Claude's outputs

2. **Copy the entire `frontend` folder** to:
   ```
   C:\Users\rocca\PycharmProjects\PythonPHMS\
   ```

3. **Open PowerShell** in the frontend directory:
   ```powershell
   cd C:\Users\rocca\PycharmProjects\PythonPHMS\frontend
   ```

4. **Install dependencies**:
   ```powershell
   npm install
   ```

5. **Run the development server**:
   ```powershell
   npm run dev
   ```

6. **Open your browser** to:
   ```
   http://localhost:3002
   ```

## File Structure

After copying, you should have:

```
C:\Users\rocca\PycharmProjects\PythonPHMS\
└── frontend\
    ├── src\
    │   ├── components\
    │   │   ├── DashboardTab.tsx
    │   │   ├── InputTab.tsx
    │   │   ├── LlmInsightsTab.tsx
    │   │   ├── OutputTab.tsx
    │   │   ├── SettingsTab.tsx
    │   │   ├── TabNavigation.tsx
    │   │   ├── TrendsTab.tsx
    │   │   ├── input-types.ts
    │   │   ├── output-types.ts
    │   │   ├── settings-types.ts
    │   │   ├── tab-navigation-types.ts
    │   │   └── trends-types.ts
    │   ├── services\
    │   │   ├── ApiClient.ts
    │   │   └── DatabaseDataProcessor.ts
    │   ├── styles\
    │   │   ├── App.css
    │   │   └── index.css
    │   ├── types\
    │   │   ├── api-types.ts
    │   │   └── app-types.ts
    │   ├── App.tsx
    │   ├── app-types.ts
    │   └── main.tsx
    ├── .eslintrc.cjs
    ├── .gitignore
    ├── index.html
    ├── package.json
    ├── README.md
    ├── tsconfig.json
    ├── tsconfig.node.json
    └── vite.config.ts
```

## Verification

After installation, verify these files exist:
- `package.json` - Contains dependencies
- `vite.config.ts` - Configures port 3002
- `src/main.tsx` - Entry point
- `src/App.tsx` - Main component

## Troubleshooting

**If `npm install` fails:**
- Ensure you're in the correct directory
- Check that `package.json` exists in the current folder
- Try running PowerShell as Administrator

**If port 3002 is in use:**
- Edit `vite.config.ts` and change the port number
- Or stop the process using port 3002

**If TypeScript errors occur:**
- Run: `npm run build` to see detailed errors
- Ensure all type files are present

## Available Commands

```powershell
npm run dev      # Start development server on port 3002
npm run build    # Build for production
npm run lint     # Run ESLint
npm run preview  # Preview production build
```

## Next Steps

Once running, the app provides:
1. **Dashboard** - Overview page
2. **Input** - Add daily/weekly data
3. **Output** - View filtered data by date range
4. **Basic Trends and Insights** - View metrics
5. **LLM Insights** - LLM integration placeholder
6. **Settings** - Configure API endpoint and table name

## Backend Connection

The frontend expects a backend API at `http://localhost:8000` by default.
You can change this in the **Settings** tab or by editing `src/App.tsx`.
