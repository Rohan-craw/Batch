import { createContext, useContext, useState } from "react";
import BASE_URL from "../../../ip/Ip";
import axios from "axios";
import { triggerFocus } from "antd/es/input/Input";





const SpecificCoordinatorContext = createContext();

const SpecificCoordinatorProvider = ({ children }) => {
    const [specificCoordinator, setSpecificCoordinator] = useState();
    const [loading, setLoading] = useState(false);
    const [specificCoordinatorStudents, setSpecificCoordinatorStudents] = useState()
    const [specificCoordinatorTrainers, setSpecificCoordinatorTrainers] = useState()
    const [activityLogs, setActivityLogs] = useState()

    const fetchSpecificCoordinator = async (coordinatorId) => {
        if (loading) return;

        // const token = localStorage.getItem('token');
        // if (!token) {
        //     console.error("No token found, user might be logged out.");
        //     return;
        // };

        setLoading(true)

        try {
            const response = await axios.get(`${BASE_URL}/api/coordinators/info/${coordinatorId}/`, 
                { headers: { 'Content-Type': 'application/json' },
                withCredentials : true
            }
            )
            const data = response?.data
            // console.log(data);
            
            setSpecificCoordinator(data);

        } catch (error) {
            console.error('Error fetching SpecificCoordinator Data', error)
        } finally {
            setLoading(false)
        };
    };


    // FETCH SPECIFIC COORDINATOR STUDENTS 
    const fetchSpecificCoordinatorStudents = async (coordinatorId) => {
        if (loading) return;

        // const token = localStorage.getItem('token');
        // if (!token) {
        //     console.error("No token found, user might be logged out.");
        //     return;
        // };

        setLoading(true)

        try {
            const response = await axios.get(`${BASE_URL}/api/coordinators/${coordinatorId}/students/`, 
                { headers: { 'Content-Type': 'application/json' }, 
                withCredentials : true
            }
            )
            const data = response?.data
            // console.log(data);
            

            setSpecificCoordinatorStudents(prevData => {
                if (JSON.stringify(prevData) !== JSON.stringify(data)) {
                    return data;
                }
                return prevData;
            })

        } catch (error) {
            console.error('Error fetching SpecificCoordinatorStudents Data', error)
        } finally {
            setLoading(false)
        }
    };


    // FETCH SPECIFIC COORDINATOR TRAINERS   
    const fetchSpecificCoordinatorTrainers = async (coordinatorId) => {
        if (loading) return;

        // const token = localStorage.getItem('token');
        // if (!token) {
        //     console.error("No token found, user might be logged out.");
        //     return;
        // };

        setLoading(true)

        try {
            const response = await axios.get(`${BASE_URL}/api/coordinators/${coordinatorId}/trainer/`, 
                { headers: { 'Content-Type': 'application/json' }, 
                withCredentials : true
            }
            )
            const data = response?.data
            // console.log(data);
            

            setSpecificCoordinatorTrainers(prevData => {
                if (JSON.stringify(prevData) !== JSON.stringify(data)) {
                    return data;
                }
                return prevData;
            })

        } catch (error) {
            console.error('Error fetching SpecificCoordinatorTrainers Data', error)
        } finally {
            setLoading(false)
        }
    };


    // FETCH COORDINATOR ACTIVITY LOGS 
    const fetchSpecificCoordinatorActivityLogs = async (coordinatorId, { page = 1, pageSize = 50, search = '', type } = {}) => {
        if (loading) return;

        // const token = localStorage.getItem('token');
        // if (!token) {
        //     console.error("No token found, user might be logged out.");
        //     return;
        // };

        setLoading(true)

        try {
            const response = await axios.get(`${BASE_URL}/api/coordinators/info/${coordinatorId}/`, 
                { headers: { 'Content-Type': 'application/json' },
                params: {
                    page,
                    page_size: pageSize,
                    search,
                    type
                },
                withCredentials : true
            }
            )
            const data = response?.data
            // console.log(data);
            
            setActivityLogs(data);

        } catch (error) {
            console.error('Error fetching SpecificCoordinator Data', error)
        } finally {
            setLoading(false)
        };
    };


    return (
        <SpecificCoordinatorContext.Provider value={{ loading, specificCoordinator, fetchSpecificCoordinator, specificCoordinatorStudents, fetchSpecificCoordinatorStudents,specificCoordinatorTrainers, fetchSpecificCoordinatorTrainers, activityLogs, fetchSpecificCoordinatorActivityLogs }}>
            {children}
        </SpecificCoordinatorContext.Provider>
    )

};

const useSpecificCoordinator = () => {
    const context = useContext(SpecificCoordinatorContext);
    if (!context) {
        throw new Error('Specific Coordinator must be used within Specific Coordinator Provider')
    }
    return context
}

export { SpecificCoordinatorProvider, useSpecificCoordinator }