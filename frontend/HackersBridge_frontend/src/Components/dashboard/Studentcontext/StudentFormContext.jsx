import axios from "axios";
import { createContext, useContext, useState } from "react"
import BASE_URL from "../../../ip/Ip";



const StudentFormContext = createContext();

const initialFormData = {
    enrollmentNumber : "",
    studentName : "",
    dateOfBirth : "",
    dateOfJoining : "",
    phoneNumber : "",
    alternatePhoneNUmber : "",
    emailAddress : "",
    studentAddress : "",
    course : [],
    language : "",
    mode : "",
    preferredWeek : "",
    location : "",
    guardianName : "",
    guardianPhoneNumber : "",
    courseCounsellor : "",
    supportCoordinator : "",
    note : "",
    // studentProfilePicture : "",
};

const StudentFormProvider = ({ children }) => {

    const [studentFormData, setStudentFormData] = useState(initialFormData);
    const [studentData, setStudentData] = useState([]);
    const [loading, setLoading] = useState(false);  // Loading state to manage fetch state
    const [errors, setErrors] = useState({});
    
    const [studentsCounts, setStudentsCounts] = useState();
    const [allStudentData, setAllStudentData] = useState([]);
    

    // Function to reset form
    const resetStudentForm = () => {
        setStudentFormData(initialFormData);
    };

    const fetchStudents = async ({ page = 1, pageSize = 30, search = '', mode = '', language = '', preferred_week = '', location = '', status = '', date_of_joining_after = '', date_of_joining_before = '' } = {}) => {
        if (loading) return;  // Prevent multiple fetches at the same time

        // const token = localStorage.getItem('token');
        // if (!token) {
        //     console.error("No token found, user might be logged out.");
        //     return;
        // };

        setLoading(true);  // Set loading state
        try {
            const response = await axios.get(`${BASE_URL}/api/students/`, 
                { headers: { 'Content-Type': 'application/json' },
                withCredentials : true,
                params: {
                    page,
                    page_size: pageSize,
                    search,
                    mode ,
                    language,
                    preferred_week,
                    location,
                    status,
                    date_of_joining_after,
                    date_of_joining_before,
                },
            }
            );
            const data = response?.data;
            // console.log(data);  

            // Update state only if data has changed
            setStudentData(prevData => {
                if (JSON.stringify(prevData) !== JSON.stringify(data)) {
                    return data;
                }
                return prevData;
            });

            // console.log('Student Data Updated:', data); //  Log new data here
        } catch (error) {
            console.error('Error fetching student Data', error);
        } finally {
            setLoading(false);  // Reset loading state after fetch
        }
    };



    const fetchStudentCount = async () => {
        if (loading) return;
        
        // const token = localStorage.getItem('token');
        // if (!token) {
        //     console.error("No token found, user might be logged out.");
        //     return;
        // };

        
        setLoading(true);
        try {
            const response = await axios.get(`${BASE_URL}/api/studentscraw/`, 
                { headers: { 'Content-Type': 'application/json' },
            withCredentials: true
            }
            );
            const data = response?.data;        
            
            setStudentsCounts(prevData => 
                JSON.stringify(prevData) !== JSON.stringify(data) ? data : prevData
            );

            // console.log('Student Count Data ', data)
        } catch (error) {
        console.error('Error fetching Batches Data', error);
        } finally {
        setLoading(false);
        }
    };


// FETCH ALL STUDENTS
const fetchAllStudent = async () => {
    if (loading) return;
    
    // const token = localStorage.getItem('token');
    // if (!token) {
    //     console.error("No token found, user might be logged out.");
    //     return;
    // };

    
    setLoading(true);
    try {
        const response = await axios.get(`${BASE_URL}/api/allstudents/`, 
            { headers: { 'Content-Type': 'application/json' }, 
            withCredentials : true
        }
        );
        const data = response?.data;        
        
        setAllStudentData(prevData => 
            JSON.stringify(prevData) !== JSON.stringify(data) ? data : prevData
        );

        // console.log('Student Count Data ', data)
    } catch (error) {
      console.error('Error fetching Batches Data', error);
    } finally {
      setLoading(false);
    }
}

    

    return (
        <StudentFormContext.Provider value={{ studentFormData, loading, setStudentFormData, errors, setErrors, resetStudentForm, studentData, setStudentData, fetchStudents, studentsCounts, fetchStudentCount, allStudentData, fetchAllStudent  }}>
            {children}
        </StudentFormContext.Provider>
    );
};


const useStudentForm = () => {
    const context = useContext(StudentFormContext);
    if(!context) {
        throw new Error("UseStudentForm must be used within a StudentFormProvider");
    }
    return context;
};

export { StudentFormProvider , useStudentForm };