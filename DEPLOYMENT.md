# Metabolical Backend - Render Deployment Guide

## 🚀 Quick Deployment Steps

### 1. Prepare Your Repository

Make sure your code is pushed to GitHub with all the new Docker files:
- `Dockerfile`
- `.dockerignore` 
- `render.yaml`
- Updated `requirements.txt`
- Updated CORS configuration in `app/main.py`

### 2. Deploy to Render

#### Option A: Automatic Deployment (Recommended)
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file
5. Review the configuration and click "Apply"

#### Option B: Manual Deployment
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure the following settings:
   - **Environment**: Docker
   - **Build Command**: (leave empty - Docker handles this)
   - **Start Command**: (leave empty - Docker handles this)
   - **Dockerfile Path**: ./Dockerfile

### 3. Environment Variables

Add these environment variables in Render:

```
PORT=8000
HOST=0.0.0.0
PYTHONUNBUFFERED=1
RENDER=true
CORS_ORIGINS=https://your-frontend-domain.com,https://localhost:3000,http://localhost:3000
```

**Important**: Replace `https://your-frontend-domain.com` with your actual frontend URL!

### 4. Update Frontend Configuration

In your frontend project, create a `.env.production` file:

```env
VITE_BACKEND_API=https://your-backend-name.onrender.com/api/v1
```

Replace `your-backend-name` with your actual Render service name.

## 🔧 Local Testing with Docker

Test your Docker setup locally before deploying:

```bash
# Build the Docker image
docker build -t metabolical-backend .

# Run the container
docker run -p 8000:8000 -e CORS_ORIGINS="http://localhost:3000" metabolical-backend

# Test the API
curl http://localhost:8000/api/v1/health
```

## 🌐 Frontend Deployment

### Deploy Frontend to Render

1. Create a new Web Service for your frontend
2. Set build command: `npm run build`
3. Set publish directory: `dist`
4. Add environment variable: `VITE_BACKEND_API=https://your-backend-name.onrender.com/api/v1`

### Deploy Frontend to Vercel/Netlify

1. Connect your frontend repository
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Add environment variable: `VITE_BACKEND_API=https://your-backend-name.onrender.com/api/v1`

## 🔍 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Make sure your frontend domain is added to `CORS_ORIGINS`
   - Check that the backend URL in frontend is correct

2. **Database Issues**
   - The SQLite database is included in the Docker image
   - For production, consider migrating to PostgreSQL

3. **Timeout Issues**
   - Render free tier has cold start delays
   - Consider upgrading to paid tier for better performance

### Health Check

Your API includes a health check endpoint: `/api/v1/health`

Test it after deployment:
```bash
curl https://your-backend-name.onrender.com/api/v1/health
```

### Logs

View logs in Render dashboard:
1. Go to your service
2. Click "Logs" tab
3. Monitor for any errors

## 📚 API Endpoints

After deployment, your API will be available at:
- Health Check: `https://your-backend-name.onrender.com/api/v1/health`
- Search: `https://your-backend-name.onrender.com/api/v1/search?q=diabetes`
- Categories: `https://your-backend-name.onrender.com/api/v1/categories`
- Category Articles: `https://your-backend-name.onrender.com/api/v1/category/diseases`
- Documentation: `https://your-backend-name.onrender.com/docs`

## 🔒 Security Notes

- CORS is configured for production with specific origins
- Docker container runs as non-root user
- Health checks are enabled
- Production logging is configured

## 🚀 Performance Tips

1. **Upgrade Render Plan**: Free tier has limitations
2. **Enable Auto-scaling**: For higher traffic
3. **Use CDN**: For static assets
4. **Database Optimization**: Consider PostgreSQL for production
5. **Caching**: Implement Redis for frequently accessed data

## 📱 Next Steps

1. Deploy both backend and frontend
2. Test all API endpoints
3. Update CORS origins with actual frontend URL
4. Monitor performance and logs
5. Set up database backups (if using external DB)
6. Configure custom domain (optional)

## 🆘 Support

If you encounter issues:
1. Check Render service logs
2. Verify environment variables
3. Test endpoints manually
4. Check CORS configuration
5. Review Docker build logs
