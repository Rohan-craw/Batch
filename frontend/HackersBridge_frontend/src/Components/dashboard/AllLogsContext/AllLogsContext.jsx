import axios from "axios";
import React, { createContext, useState, useContext, useCallback, useMemo } from "react";
import BASE_URL from "../../../ip/Ip";

// Create the context object
const AllLogsContext = createContext();


const AllLogsProvider = ({ children }) => {
  const [allLogsData, setAllLogsData] = useState();
  const [loading, setLoading] = useState(false);


    const fetchAllLogs = useCallback (async ({ page = 1, pageSize = 100, search = '' } = {}) => {
        if (loading) return;
       
        // const token = localStorage.getItem('token');
        // if (!token) {
        //     console.error("No token found, user might be logged out.");
        //     return;
        // };

        setLoading(true);
        try {
            const response = await axios.get(`${BASE_URL}/api/logs/`,
            { headers: { 'Content-Type': 'application/json'},
            params: {
              page,
              page_size: pageSize,
              search,
          },
            withCredentials : true
          }
            );
            const data = response.data;
            // console.log(data);
            
            setAllLogsData(prevData => {
              if(JSON.stringify(prevData) !== JSON.stringify(data)){
                return data;
              };
              return prevData;
            });

            // console.log('Batches Data ', data)
        } catch (error) {
          console.error('Error fetching All Logs Data', error);
        } finally {
          setLoading(false);
        }
    }, [loading]);


  return (
    <AllLogsContext.Provider value={{ loading, allLogsData, setAllLogsData, fetchAllLogs }}>
      {children}
    </AllLogsContext.Provider>
  );
};

// Custom hook to access context
const useAllLogs = () => {
  const context = useContext(AllLogsContext);
  if (!context) {
    throw new Error("All Logs must be used within a AllLogsProvider");
  }
  return context;
};

export { AllLogsProvider, useAllLogs }; // Named exports
