const { Kafka , CompressionTypes} = require('kafkajs');
const fs = require('fs');
const axios = require('axios');
const https = require('https');
const { iam_url, client_id, client_psw, bootstrap_external } = require('./variable.js');
const kafkaBrokers = [bootstrap_external];
async function getAccessToken() {
  const oauthProviderUrl = iam_url;
  const clientId = client_id;
  const clientSecret = client_psw;
  const httpsAgent = new https.Agent({ rejectUnauthorized: false });
  const axiosConfig = {
    httpsAgent,
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  };
    const response = await axios.post(oauthProviderUrl, {
      grant_type: 'client_credentials',
      client_id: clientId,
      client_secret: clientSecret,
    },axiosConfig);

    if (response.status === 200) {
      return response.data.access_token;
    } else {
      throw new Error('Unable to obtain access token');
    }
}
const sendMessage = async (topicMessage,count) => {
  const kafka = new Kafka({
  brokers: kafkaBrokers,
  ssl: {
    // Path to the CA certificate file
    ca: [fs.readFileSync('/var/tmp/serverca.crt', 'utf-8')],
  },
  sasl: {
    mechanism: 'oauthbearer',
    // Additional OAuth properties
    oauthBearerProvider: async () => {
      // Implement the logic to obtain and return the OAuth token here
      // You might use a library like 'axios' to request an access token
      const accessToken = await getAccessToken();
      return {
        value: accessToken,
      };
    },
  },
});
const startTime = new Date();
const producer = kafka.producer();

  try {
    await producer.connect();
    const ProducerStartTime = new Date();
    console.log("Producer start time "+ProducerStartTime)
    for (let i = 1; i <= count; i++) {
    await producer.sendBatch({
      topicMessages: topicMessage,
      acks: 0,
      compression: CompressionTypes.CODEC_LZ4,
    });
    //console.log(`Message sent: ${topicMessage} ${i}`);
  }
      // Get the current date and time as the end time
    const endTime = new Date();
    console.log("Producer end time "+endTime)

    // Calculate the elapsed time in milliseconds
    const elapsedTime = endTime - startTime;
    const jsonResponse = {
      message: topicMessage,
      timetaken: elapsedTime
    };
    return jsonResponse;
  } catch (error) {
    console.error('Error sending message:', error);
  } finally {
    await producer.disconnect();
  }
};
module.exports = sendMessage;


