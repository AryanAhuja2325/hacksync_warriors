const axios = require('axios');

const IG_ACCESS_TOKEN = process.env.IG_ACCESS_TOKEN || process.env.IG_KEY;
const IG_ACCOUNT_ID = process.env.IG_ACCOUNT_ID || '17841478156117645';

/**
 * Get Instagram account insights/metrics
 */
const getAccountInsights = async (req, res) => {
  try {
    const { period = 'day', since, until } = req.query;

    if (!IG_ACCESS_TOKEN) {
      return res.status(500).json({ 
        msg: 'Instagram API key not configured. Set IG_ACCESS_TOKEN in environment variables.' 
      });
    }

    // Fetch user profile info
    let profileInfo = {};
    try {
      const profileResponse = await axios.get(
        `https://graph.instagram.com/v21.0/${IG_ACCOUNT_ID}`,
        {
          params: {
            fields: 'username,name,profile_picture_url,followers_count,follows_count,media_count,biography,website',
            access_token: IG_ACCESS_TOKEN
          }
        }
      );
      profileInfo = profileResponse.data;
    } catch (err) {
      console.warn('Could not fetch profile info:', err.message);
    }

    // Comprehensive metrics based on period
    const allDayMetrics = [
      'reach', 'impressions', 'profile_views', 'follower_count', 
      'website_clicks', 'online_followers', 'accounts_engaged', 
      'total_interactions', 'profile_links_taps', 'likes', 'comments', 
      'shares', 'saves', 'replies', 'follows_and_unfollows'
    ];
    
    const weekMetrics = [
      'reach', 'impressions', 'profile_views', 'follower_count',
      'accounts_engaged', 'total_interactions'
    ];
    
    const metrics = period === 'day' ? allDayMetrics : weekMetrics;

    const params = {
      metric: metrics.join(','),
      period,
      access_token: IG_ACCESS_TOKEN
    };

    if (since) params.since = since;
    if (until) params.until = until;

    console.log('Fetching Instagram insights...');
    const insightsResponse = await axios.get(
      `https://graph.instagram.com/v21.0/${IG_ACCOUNT_ID}/insights`,
      { params }
    );

    // Initialize all metrics with 0 values
    const insights = {};
    metrics.forEach(metricName => {
      insights[metricName] = {
        value: 0,
        title: metricName.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
        description: '',
        period: period
      };
    });

    // Update with actual values from API
    insightsResponse.data.data.forEach(metric => {
      insights[metric.name] = {
        value: metric.values[0]?.value || 0,
        title: metric.title,
        description: metric.description,
        period: metric.period
      };
    });

    res.json({
      success: true,
      profile: profileInfo,
      insights,
      period,
      fetchedAt: new Date()
    });

  } catch (error) {
    console.error('Instagram insights error:', error.response?.data || error.message);
    
    const errorMessage = error.response?.data?.error?.message || error.message || 'Failed to fetch insights';
    
    res.status(error.response?.status || 500).json({
      msg: errorMessage,
      error: error.response?.data
    });
  }
};

module.exports = {
  getAccountInsights
};
