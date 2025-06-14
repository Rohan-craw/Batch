import React, { useEffect, useState } from 'react';
import { Card, Col, Row } from 'antd';


import { useAllLogs } from '../AllLogsContext/AllLogsContext';

const LogsCountCards = () => {
    const { allLogsData, fetchAllLogs } = useAllLogs();


    useEffect(() => {
        fetchAllLogs(); 
        // console.log(allLogsData);
        
        }, []);
        const coordinatorCounts = allLogsData?.log_counts_by_coordinator || [];
        // console.log(coordinatorCounts);


    return (
        <Row gutter={14}>
            {coordinatorCounts.map(({ actor__username, log_count, actor__first_name }) => (
            <Col span={6} key={actor__username}>
            <Card
                title={actor__first_name || actor__username}
                variant="borderless"
                className="font-semibold cursor-pointer text-blue-500 text-lg mb-2"
            >
                {log_count}
            </Card>
            </Col>
            ))}
      </Row>
    )
}
export default LogsCountCards;