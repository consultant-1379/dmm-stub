const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const consumeMessages = require('./consumer.js')
const sendMessage = require('./producer.js')
const app = express();
const port = 3000;
const host = '0.0.0.0'; 

app.use(bodyParser.json());
app.use(cors());
app.use((error, req, res, next) => {
    if (error instanceof SyntaxError && error.status === 400 && 'body' in error) {
     console.log("sent wrong type payload")
      res.status(400).json({ error: 'Input data should be only JSON format' });
    } else {
      next();
    }
  });
app.post('/consume/:count', async (req, res) => {
    const inputCount = Math.floor(parseFloat(req.params.count));
    if(inputCount == 0){
      console.log("count of the message should not be empty")
      return res.status(400).json({ error: 'count of the message should not be empty' });
    }
    if (isNaN(inputCount)) {
      return res.status(400).json({ error: 'Invalid input count' });
    }
    let input = req.body;
    console.log(input)
    let inputTopic = input.topics
    let inputConsumer = input.consumer
    try {
      const messagess=await consumeMessages(inputTopic,inputCount,inputConsumer);
      res.status(200).json(messagess);
    } catch (error) {
      const statusCode = error.statusCode || 500;
      res.status(statusCode).json({ success: false, error: error.message });
    }
  });

app.post('/produce/:count', async (req, res) => {
    const inputCount = Math.floor(parseFloat(req.params.count));
    if(inputCount == 0){
      console.log("count of the message should not be empty")
      return res.status(400).json({ error: 'count of the message should not be empty' });
    }
    if (isNaN(inputCount)) {
      return res.status(400).json({ error: 'Invalid input count' });
    }
     const messageToSend = req.body;
     //console.log(messageToSend)
    try {
      const messagess=await sendMessage(messageToSend,inputCount);
      res.status(200).json(messagess);
    } catch (error) {
      console.error('Error producing message:', error);
      res.status(401).json({ error: 'An error occurred' });
    }
  });

app.listen(port,host, () => {
  console.log(`Server is running on port ${host};${port}`);
});
