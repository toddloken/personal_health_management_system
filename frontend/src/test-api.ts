import { ApiClient } from './api/ApiClient';

const client = new ApiClient({
    baseUrl: 'http://127.0.0.1:8000',
    timeout: 30000
});

async function testQuery() {
    console.log('Testing API query...');

    const result = await client.queryData({
        table_name: 'personal_data',
        start_date: '2025-11-22',
        end_date: '2025-11-29'
    });

    console.log('Success:', result.success);
    console.log('Row count:', result.data.row_count);
    console.log('Columns:', result.data.columns);
    console.log('First row:', result.data.data[0]);
}

testQuery();