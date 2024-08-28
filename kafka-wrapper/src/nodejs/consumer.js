const { Kafka } = require('kafkajs');
const fs = require('fs');
const axios = require('axios');
const https = require('https');
const { iam_url, client_id, client_psw, bootstrap_external } = require('./variable.js');
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
async function consumeMessages(topic_name ,maxMessages,ConsumerGroup) {
const kafka = new Kafka({
  clientId: 'my-kafka-consumer',
  brokers: [bootstrap_external], // Replace with your Kafka broker addresses
  ssl: {
    // Path to the CA certificate file
    ca: [fs.readFileSync('/var/tmp/serverca.crt', 'utf-8')],
  },
  sasl: {
    mechanism: 'oauthbearer',
    // Additional OAuth properties
    oauthBearerProvider: async () => {
      // Implement the logic to obtain and return the OAuth token here
      const accessToken = await getAccessToken(); // Make sure to implement this function
      return {
        value: accessToken,
      };
    },
  },
});
const consumer = kafka.consumer({ groupId: ConsumerGroup ,minBytes: 100000,maxWaitTimeInMs: 500});
const numberOfMessagesToConsume = maxMessages
let messagesConsumed = 0;
let elapsedTime =0;
const startTime = new Date();
let foundTargetMessage = false;
const messages = [];
  await consumer.connect();
  await consumer.subscribe({ topics: topic_name, fromBeginning: true });

const consumerPromise = new Promise((resolve, reject) => {
  console.log("Consumer listioning")
  let ConsumerStartTime=new Date();
  console.log("consumer start time "+ConsumerStartTime)
  consumer.run({
    partitionsConsumedConcurrently: 3,
    eachMessage: async ({ topic, partition, message }) => {
      // Message handling logic
      // console.log(`Received message from topic ${topic}, partition ${partition}:`);
      // console.log(JSON.parse(message.value.toString()));
      messages.push(message.value.toString());
      messagesConsumed++;
      // console.log("consumed message is :"+messagesConsumed+"  total message is : "+numberOfMessagesToConsume)
      if (messagesConsumed === numberOfMessagesToConsume) {
        // Get the current date and time as the end time
        const endTime = new Date();
        console.log("consumer end time "+endTime)
        // Calculate the elapsed time in milliseconds
        elapsedTime = endTime - startTime;
        console.log(`Found the target message: "${messagesConsumed}"`);
        consumer.disconnect().then(resolve);
      }
    },
  });
});
await consumerPromise;
const total_message=numberOfMessagesToConsume*topic_name.length
const jsonResponse = {
  message: "Consumed "+total_message+" messages",
  timetaken: elapsedTime
};
return jsonResponse;
};
module.exports = consumeMessages;


