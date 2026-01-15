const axios = require('axios');

const IG_ACCESS_TOKEN = process.env.IG_ACCESS_TOKEN || process.env.IG_KEY;
const IG_ACCOUNT_ID = process.env.IG_ACCOUNT_ID || '17841478156117645';

/**
 * Post image to Instagram using two-step process:
 * 1. Create media container
 * 2. Publish media
 */
const postToInstagram = async (req, res) => {
  try {
    const { image_url, caption } = req.body;

    if (!image_url) {
      return res.status(400).json({ msg: 'Image URL is required' });
    }

    if (!IG_ACCESS_TOKEN) {
      return res.status(500).json({ 
        msg: 'Instagram API key not configured. Set IG_ACCESS_TOKEN in environment variables.' 
      });
    }

    // Step 1: Create media container
    console.log('Step 1: Creating Instagram media container...');
    const containerResponse = await axios.post(
      `https://graph.instagram.com/v21.0/${IG_ACCOUNT_ID}/media`,
      {
        image_url,
        caption: caption || ''
      },
      {
        headers: {
          'Authorization': `Bearer ${IG_ACCESS_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const creationId = containerResponse.data.id;
    console.log('Media container created:', creationId);

    // Step 1.5: Wait for container to be ready (poll status)
    console.log('Waiting for media container to be ready...');
    await waitForContainerReady(creationId);

    // Step 2: Publish the media
    console.log('Step 2: Publishing media to Instagram...');
    const publishResponse = await axios.post(
      `https://graph.instagram.com/v21.0/${IG_ACCOUNT_ID}/media_publish`,
      {
        creation_id: creationId
      },
      {
        headers: {
          'Authorization': `Bearer ${IG_ACCESS_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const postId = publishResponse.data.id;
    console.log('Successfully posted to Instagram:', postId);

    res.json({
      success: true,
      postId,
      message: 'Successfully posted to Instagram',
      creationId
    });

  } catch (error) {
    console.error('Instagram posting error:', error.response?.data || error.message);
    
    const errorMessage = error.response?.data?.error?.message || error.message || 'Failed to post to Instagram';
    const errorCode = error.response?.data?.error?.code;

    res.status(error.response?.status || 500).json({
      msg: errorMessage,
      error: errorCode,
      details: error.response?.data
    });
  }
};

/**
 * Wait for Instagram media container to be ready for publishing
 * Polls the container status until it's FINISHED or times out
 */
const waitForContainerReady = async (containerId, maxAttempts = 10, delayMs = 2000) => {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const statusResponse = await axios.get(
        `https://graph.instagram.com/v21.0/${containerId}`,
        {
          params: {
            fields: 'status_code',
            access_token: IG_ACCESS_TOKEN
          }
        }
      );

      const statusCode = statusResponse.data.status_code;
      console.log(`Container status check (${attempt}/${maxAttempts}): ${statusCode}`);

      if (statusCode === 'FINISHED') {
        console.log('Container is ready for publishing!');
        return true;
      }

      if (statusCode === 'ERROR') {
        throw new Error('Media container processing failed');
      }

      // Wait before next attempt
      if (attempt < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    } catch (error) {
      console.warn(`Status check attempt ${attempt} failed:`, error.message);
      if (attempt < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
  }

  throw new Error('Media container did not become ready in time. Please try again later.');
};

module.exports = {
  postToInstagram
};
