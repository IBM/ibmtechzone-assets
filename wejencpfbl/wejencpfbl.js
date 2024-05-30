require('dotenv').config();
const COS = require('ibm-cos-sdk');
const { program } = require('commander');
const path = require('path');

// Load configuration from environment variables
const config = {
    endpoint: process.env.ENDPOINT,
    apiKeyId: process.env.API_KEY_ID,
    serviceInstanceId: process.env.SERVICE_INSTANCE_ID,
    bucketName: process.env.BUCKET_NAME,
};

// Configure IBM COS
const cos = new COS.S3({
    endpoint: config.endpoint,
    apiKeyId: config.apiKeyId,
    ibmAuthEndpoint: 'https://iam.cloud.ibm.com/identity/token',
    serviceInstanceId: config.serviceInstanceId,
});

// Fetch logs from ICOS
async function fetchLogs(date) {
    const prefix = `events_logs/${date}/`;
    // console.log(`Using bucket: ${config.bucketName}`);
    // console.log(`Using prefix: ${prefix}`);
    
    try {
        const objects = await cos.listObjectsV2({ Bucket: config.bucketName, Prefix: prefix }).promise();
        const keys = objects.Contents.map(obj => obj.Key);
        // console.log(`Fetched keys: ${JSON.stringify(keys, null, 2)}`);
        return keys;
    } catch (error) {
        console.error('Error fetching logs:', error);
        return [];
    }
}

// Get log content
async function getLogContent(key) {
    try {
        const data = await cos.getObject({ Bucket: config.bucketName, Key: key }).promise();
        const log = JSON.parse(data.Body.toString('utf-8'));
        // console.log(`Fetched log content for ${key}: ${JSON.stringify(log, null, 2)}`);
        return log;
    } catch (error) {
        console.error(`Error fetching log content for ${key}:`, error);
        return null;
    }
}

// Process logs
async function processLogs(date) {
    const keys = await fetchLogs(date);
    if (keys.length === 0) {
        console.log('No logs found for the given date.');
        return;
    }

    const logs = await Promise.all(keys.map(getLogContent));
    const validLogs = logs.filter(log => log !== null);

    const summary = validLogs.reduce((acc, log) => {
        if (log.event === 'Logged in') {
            acc.total++;
            if (log.user_id) {
                acc.users[log.user_id] = (acc.users[log.user_id] || 0) + 1;
            }
        }
        return acc;
    }, { total: 0, users: {} });

    const dateObj = new Date(date.substr(0, 4), date.substr(4, 2) - 1, date.substr(6, 2));
    console.log(`Access status on ${dateObj.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}`);
    console.log(`Total accesses: ${summary.total} times`);
    Object.keys(summary.users).forEach(user => {
        console.log(`${user}: ${summary.users[user]} time${summary.users[user] > 1 ? 's' : ''}`);
    });
}

// Set up CLI
program
    .version('1.0.0')
    .description('CLI tool to process logs from IBM COS')
    .option('-d, --date <date>', 'Date to fetch logs for (YYYYMMDD format)')
    .action((options) => {
        if (options.date) {
            processLogs(options.date).catch(console.error);
        } else {
            console.error('Please provide a date.');
        }
    });

program.parse(process.argv);
