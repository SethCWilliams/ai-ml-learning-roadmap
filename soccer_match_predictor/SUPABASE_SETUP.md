# Supabase Database Setup Guide

This guide walks you through setting up Supabase as the database backend for the Soccer Match Predictor.

## Quick Setup (5 minutes)

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/log in
2. Click "New Project" 
3. Choose your organization
4. Enter project details:
   - **Name**: `soccer_stats` (or any name you prefer - generic names are great for reusability!)
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to you
5. Wait 2-3 minutes for project creation

### 2. Get Connection Details

1. In your Supabase dashboard, go to **Settings > API**
2. Copy these values:
   - **Project URL** (e.g., `https://abcd1234.supabase.co`)
   - **anon/public key** (starts with `eyJhbGc...`)
   - **service_role key** (starts with `eyJhbGc...`) - keep this secret!

### 3. Create Environment File

Create a `.env` file in the project root:

```bash
# Copy from .env.example
cp .env.example .env
```

Edit `.env` with your Supabase details:

```bash
# Supabase Configuration  
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_key_here

# Cache Settings (optional - defaults shown)
CACHE_DURATION_HOURS=6
FIXTURES_CACHE_HOURS=1
STATS_CACHE_HOURS=24
```

### 4. Create Database Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Copy the entire contents of `database_schema.sql`
3. Paste into the SQL editor and click **Run**
4. You should see "Success. No rows returned" message
5. Go to **Table Editor** to verify tables were created

Expected tables:
- `leagues` (2 rows: Premier League, MLS)
- `teams` (empty)
- `fixtures` (empty)  
- `team_season_stats` (empty)
- `players` (empty)
- `player_stats` (empty)
- `predictions` (empty)
- `api_cache` (empty)

### 5. Install Dependencies

```bash
# Install the new dependency
pip install supabase>=2.0.0

# Or install all dependencies
pip install -r requirements.txt
```

## Test the Integration

Run a quick test to verify everything works:

```bash
python -c "
from src.data.database import get_database_client
db = get_database_client()
print('Database health check:', db.health_check())
print('Leagues:', db.get_leagues())
"
```

Expected output:
```
Database health check: {'status': 'healthy', 'connection': 'ok', ...}
Leagues: [{'id': 1, 'name': 'Premier League', 'code': 'EPL', ...}, ...]
```

## Performance Benefits

With Supabase caching enabled, you should see:

- **Before**: 56+ API calls per prediction
- **After**: ~10 API calls per prediction  
- **Cache hits**: 80-90% reduction in ESPN API requests
- **Speed**: Significantly faster repeated predictions

## Caching Strategy

| Data Type | Cache Duration | Reason |
|-----------|----------------|--------|
| Fixtures | 1 hour | Live scores change frequently |
| Season Stats | 24 hours | Updated daily |
| Team Schedules | 6 hours | Updated periodically |
| General API | 6 hours | Default for other endpoints |

## Troubleshooting

### "Missing Supabase configuration" Error
- Check your `.env` file has the correct `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- Make sure `.env` is in the project root directory

### "Failed to initialize database client" Error  
- Verify your Supabase project is running (green status in dashboard)
- Check your API keys are correct and not expired
- Try the service role key if anon key doesn't work

### "Table doesn't exist" Error
- Make sure you ran the `database_schema.sql` script completely
- Check the SQL Editor for any error messages
- Verify tables exist in Table Editor

### Performance Issues
- Check cache statistics: `db.get_cache_stats()`
- Clear old cache entries: `db.clear_cache()`
- Monitor Supabase dashboard for API usage

## Free Tier Limits

Supabase free tier provides:
- ✅ **Unlimited tables** (we use 8)
- ✅ **500 MB database** (plenty for our cache)
- ✅ **2 GB bandwidth/month** (sufficient for development)
- ✅ **No API request limits**

You should be well within limits for development and testing.

## Next Steps

Once Supabase is set up and working:

1. ✅ Database caching is automatically enabled
2. ✅ ESPN API calls are reduced by 80-90%  
3. ✅ Prediction results are stored for analysis
4. 🔄 Run predictions as normal - caching happens transparently

The predictor will now use cached data when available and only make fresh API calls when needed!

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your setup with the test script
3. Check Supabase dashboard for error logs
4. Review the application logs for detailed error messages