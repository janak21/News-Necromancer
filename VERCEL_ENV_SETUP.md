# Vercel Environment Setup for GhostRevive

To make the application work over the internet, you must configure the **Environment Variables** in your Vercel dashboard.

## 1. Get your API Key
Ensure you have your **OpenRouter API Key**. If you don't have one, get it from [openrouter.ai](https://openrouter.ai).

## 2. Add to Vercel
1. Go to your [Vercel Dashboard](https://vercel.com/dashboard).
2. Select your project (**news-necromancer** or similar).
3. Click on **Settings** tab.
4. Click on **Environment Variables** in the left sidebar.
5. Add a new variable:
   - **Key:** `OPENROUTER_API_KEY`
   - **Value:** `sk-or-v1-...` (your actual key)
   - **Environments:** Select Production, Preview, and Development.
6. Click **Save**.

## 3. Redeploy
After adding the variable, you **MUST redeploy** for it to take effect:
1. Go to the **Deployments** tab.
2. Click the three dots (`...`) next to your latest deployment.
3. Select **Redeploy**.
4. Check the "Redeploy" checkbox to confirm.

## Troubleshooting 500 Errors
If you still see "Server Error (500)":
1. **Check Logs:** Go to Dashboard -> Deployments -> [Latest] -> **Functions** tab -> Click on `api/feeds/process`.
2. Look for "OPENROUTER_API_KEY environment variable is missing".
3. If you see "Task timed out", the request took longer than 10 seconds. The latest update optimizes this, but trying fewer feeds might help.
