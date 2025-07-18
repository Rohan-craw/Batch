import { useEffect, useMemo, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Button, message, Popconfirm, Avatar, Tooltip, Select, Tag, Dropdown, Badge, Spin, Empty, Pagination } from 'antd';
import { EditOutlined, DeleteOutlined, DownOutlined, CopyOutlined, RightOutlined, FilterOutlined, LinkOutlined } from '@ant-design/icons';
import  { useBatchForm }  from "../Batchcontext/BatchFormContext";
import CreateBatchForm from "./CreateBatchForm";
import axios from "axios";
import BASE_URL from "../../../ip/Ip";
import AvailableBatches from "./AvailableBatches";
import { useCourseForm } from "../Coursecontext/CourseFormContext";
import { useAuth } from "../AuthContext/AuthContext";
import handleBatchClick, { handleTrainerClick } from "../../Navigations/Navigations";
import dayjs from "dayjs";
import BatchCards from "../SpecificPage/Cards/Batch/BatchCards";
import useBatchStatusChange from "../../Functions/BatchStatusChange";
import SearchBar from "../../SearchInput/SearchInput";



const Batches = () => {
    const [isModalOpen, setIsModalOpen] = useState(false); 
    const [activeTab, setActiveTab] = useState("Running");
    const [selectedBatch, setSelectedBatch] = useState();
    const [isDeleted, setIsDeleted] = useState(false)
    const [students, setStudents] = useState({}); // Stores selected students per batch
    const [selectedStudent, setSelectedStudent] = useState({}); // Stores selected students per batch
    const [addStudentDropdown, setAddStudentDropdown] = useState({});
    const [sortByTime, setSortByTime] = useState(false); // Default ascending
    const [sortByStartDate, setSortByStartDate] = useState(false);
    const [sortByEndDate, setSortByEndDate] = useState(false);
    const [sortByMode, setSortByMode] = useState(null);
    const [sortByLanguage, setSortByLanguage] = useState(null);
    const [sortByPreferredWeek, setSortByPreferredWeek] = useState(null);
    const [sortByLocation, setSortByLocation] = useState(null);
    // const [sortByCourse, setSortByCourse] = useState(null);
    
    const { batchData, loading, setLoading, setBatchData, fetchBatches } = useBatchForm();
    const { handleBatchStatusChange } = useBatchStatusChange();


    const navigate = useNavigate();

    // for Pagination 
    const [searchTerm, setSearchTerm] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const pageSize = 30;

    const handleTabClick = (tab) => {
        setActiveTab(tab);
        setCurrentPage(1)
    };


   const currentFilters = useMemo(() => ({
    page: currentPage,
    pageSize,
    search: searchTerm,
    mode: sortByMode,
    language: sortByLanguage,
    preferred_week: sortByPreferredWeek,
    location: sortByLocation,
    status: activeTab
}), [currentPage, pageSize, searchTerm, sortByMode, sortByLanguage, sortByPreferredWeek, sortByLocation, activeTab]);

      
    useEffect(() => {
        fetchBatches( currentFilters )        
    },[isModalOpen, currentFilters]);



    // Function to handle Edit button click 
    const handleEditClick = (batch) => {
        setSelectedBatch(batch);
        setIsModalOpen(true);
        setIsDeleted(false);
        setAddStudentDropdown(true);
    };


    
    // Delete Function 
    const handleDelete = async (batchId) => {
        if (!batchId) return;

        try {
            const response = await axios.delete(`${BASE_URL}/api/batches/delete/${batchId}/`, 
                { headers: { 'Content-Type': 'application/json' },
                withCredentials : true
            }
            );

            if (response.status >= 200 && response.status < 300) {
                // Only update the batch data if it's correctly structured
                if (
                    batchData?.results &&
                    Array.isArray(batchData.results.batches)
                ) {
                    setBatchData(prevBatch => {
                        const updatedBatches = prevBatch.results.batches.filter(
                            batch => String(batch.id) !== String(batchId)
                        );
    
                        // Update the batches in the corresponding status category
                        return {
                            ...prevBatch,
                            results: {
                                ...prevBatch.results,
                                batches: updatedBatches, // Update the batches array
                            },
                        };
                    });
            
                    setTimeout(() => {
                        setSearchTerm('');
                    }, 2000);
                } else {
                    console.error('batchData is not an array or properly structured');
                }
            } else {
                message.error('Failed to delete batch');
            }
            
   
        } catch (error) {
            setLoading(false);
        
            if (error.response) {
                console.error("Server Error Response:", error.response.data);
        
                // Extract error messages and show each one separately
                Object.entries(error.response.data).forEach(([key, value]) => {
                    value.forEach((msg) => {
                        message.error(`${msg}`);
                    });
                });
            } else if (error.request) {
                console.error("No Response from Server:", error.request);
                message.error("No response from server. Please check your internet connection.");
            } else {
                console.error("Error Message:", error.message);
                message.error("An unexpected error occurred.");
            }
        }       
    };


    // Confirm and Cancel Handler for delete button 
    const confirm = (batchId) => {
        handleDelete(batchId);
    };

    const cancel = () => {
        message.error('batch Deletion Cancelled');
    };


    // to add students in a batch fetch available student data from select field
    const fetchAvailableStudents = useCallback(async (batchId) => {
        try {
            const response = await axios.get(`${BASE_URL}/api/batches/${batchId}/available-students/`, 
                { headers: { 'Content-Type': 'application/json' },
                withCredentials : true
            }
            );
            const data = response.data;
            // console.log(data);
            
            if (!data.available_students) {
                throw new Error("Invalid response format");
            }
    
            // Format data for the Select component
            const formattedOptions = data.available_students.map(student => ({
                name: student.name,
                studentid: student.id,
                phone: student.phone
            }));
            
    
            // Update state with students for the specific batchId
            setStudents(prev => ({ ...prev, [batchId]: formattedOptions }));
        } catch (error) {
            console.error("Error fetching students:", error);
        }
    }, [students]) 
    

    // send student id to api and add it in selected  batch
    const addStudents = async (batchId) => {
        
        // Get selected student IDs for this batch
        const studentIds = selectedStudent[batchId] || [];
        // console.log("Batch ID:", batchId, studentIds);
    
        if (studentIds.length === 0) {
            message.warning("No students selected!");
            return;
        }
    
        try {
            const response = await axios.post(`${BASE_URL}/api/batches/${batchId}/add-students/`, 
                { students: studentIds }, // Ensure correct payload format
                { headers: { 'Content-Type': 'application/json'},
                withCredentials : true
            }
            );
    
            if (response.status >= 200 && response.status < 300) {
                message.success("Student added successfully!");
                setAddStudentDropdown(false); // Close dropdown on success
                await fetchBatches(currentFilters);
            } else {
                message.error("Student not added.");
            }
        } catch (error) {
            // console.error("Error sending Add student request:", error);
            message.error("Failed to add student.");
        }
    };
    
    

    const handleSelectChange = (batchId, selectedValues) => {
        setSelectedStudent(prev => ({
            ...prev,
            [batchId]: selectedValues // Store selected student IDs
        }));
    };
    

    const handleStudentDropdown = (batchId, index) => {
        
        if (addStudentDropdown === index) {
            setAddStudentDropdown(null); // Close dropdown
        } else {
            setAddStudentDropdown(index);
            if (!selectedStudent[index]) fetchAvailableStudents(batchId, index); // Fetch only if not already loaded
        }
    };


    // HANDLE STATUS CHANGE OF BATCH 
    // const handleBatchStatusChange = async (batchId, status) => {
    //     if (!batchId || !status) return;

    //         // Get today's date in YYYY-MM-DD format
    //             const today = new Date().toISOString().split("T")[0];
        
    //         // If status is "Completed" or "Cancelled", set batch_end_date to today
    //         const updatedData = {
    //             status,
    //             ...(status === "Completed" || status === "Cancelled" ? { end_date: today } : {}),
    //         };
                
    //     try {
    //         const response = await axios.put(`${BASE_URL}/api/batches/edit/${batchId}/`,
    //             JSON.stringify(updatedData),
    //             { headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    //             withCredentials : true
    //         }
    //         );
            
    //         if (response.status >= 200 && response.status < 300) {
    //             message.success(`Batch status updated successfully to ${status} !`);
    //             // console.log(updatedData);
                
    //         } else {
    //             message.error("Batch status not updated.");
    //         };
            
    //        await fetchBatches(currentFilters)
    
    //     } catch (error) {
    //         console.error("Error sending status data to server", error);
    //     }
    // };
    
    // Handle Toggle of batch running, scheduled, hold and completed, cancelled 
    const onChangeStatus = async (batchId, status) => {
        handleBatchStatusChange({ batchId, status });
        await fetchBatches(currentFilters)
    };


    // FOR SORTING BY START TIME AND START DATE
        const toggleSortByStartTime = () => {
            setSortByTime((prev) => !prev);
            setSortByStartDate(false); // Reset start_time sorting when sorting by name
        };
      
        const toggleSortByStartDate = () => {
            setSortByStartDate((prev) => !prev);
            setSortByTime(false); // Reset name sorting when sorting by start_time
        };

        const toggleSortByEndDate = () => {
            setSortByEndDate((prev) => !prev);
            setSortByTime(false);  // Explicitly set to false instead of null
            setSortByStartDate(false);
        };
        
        
        const data = batchData?.results?.batches || [];
        
        const sortedBatches = useMemo(() => {
            let sorted = [...data];
        
            
            if (sortByTime) {
                sorted.sort((a, b) => a.batch_time_data.start_time.localeCompare(b.batch_time_data.start_time));
            }
        
            if (sortByStartDate) {
                sorted.sort((a, b) => new Date(a.start_date) - new Date(b.start_date));
            }
        
            if (sortByEndDate) {
                sorted.sort((a, b) => new Date(a.end_date) - new Date(b.end_date));
            }
        
            return sorted;
        }, [data, sortByTime, sortByStartDate, sortByEndDate]);
        


        const handleSort = async (key, filterType) => {
            if (key === "clear") {
                if (filterType === "mode") setSortByMode(null);
                if (filterType === "language") setSortByLanguage(null);
                if (filterType === "preferred_week") setSortByPreferredWeek(null);
                if (filterType === "location") setSortByLocation(null);
               
                return;
            }
        
            if (filterType === "mode") setSortByMode(key);
            if (filterType === "language") setSortByLanguage(key);
            if (filterType === "preferred_week") setSortByPreferredWeek(key);
            if (filterType === "location") setSortByLocation(key);
        
        };
        

            const modeMenu = {
                items: [
                    { key: "Online", label: <span style={{ color: "red" }}>Online</span> },
                    { key: "Offline", label: <span style={{ color: "green" }}>Offline</span> },
                    { key: "Hybrid", label: <span style={{ color: "blue" }}>Hybrid</span> },
                    { type: "divider" },
                    { key: "clear", label:  <span style={{ color: "red", fontWeight: "bold" }}>Clear Filter</span> },
                ],
                onClick: ({ key }) => handleSort(key, "mode"),
            };

            const languageMenu = {
                items: [
                    { key: "Hindi", label: <span style={{ color: "green" }}>Hindi</span> },
                    { key: "English", label: <span style={{ color: "red" }}>English</span> },
                    { key: "Both", label: <span style={{ color: "blue" }}>Both</span> },
                    { type: "divider" },
                    { key: "clear", label:  <span style={{ color: "red", fontWeight: "bold" }}>Clear Filter</span> },
                ],
                onClick: ({ key }) => handleSort(key, "language"),
            };

            const preferredWeekMenu = {
                items: [
                    { key: "Weekdays", label: <span style={{ color: "gray" }}>Weekdays</span> },
                    { key: "Weekends", label: <span style={{ color: "gray" }}>Weekends</span> },
                    { type: "divider" },
                    { key: "clear", label:  <span style={{ color: "red", fontWeight: "bold" }}>Clear Filter</span> },
                ],
                onClick: ({ key }) => handleSort(key, "preferred_week"),
            };

            const locationMenu = {
                items: [
                    { key: "Saket", label: <span style={{ color: "blue" }}>Saket</span> },
                    { key: "Laxmi Nagar", label: <span style={{ color: "magenta" }}>Laxmi Nagar</span> },
                    { type: "divider" },
                    { key: "clear", label:  <span style={{ color: "red", fontWeight: "bold" }}>Clear Filter</span> },
                ],
                onClick: ({ key }) => handleSort(key, "location"),
            };


    // THIS WILL REDIRECT TO STUDENT IONFO PAGE IN NEW TAB FROM FILTERED STUDENT SELECT FIELD
    const handleStudentClickOnSelect = (event, studentId) => {
        event.preventDefault();
        event.stopPropagation(); // Prevents interfering with Select behavior
    
        if (!studentId) return;
    
        const encodedStudentId = btoa(studentId);
        
        // Open in a new tab without switching focus immediately
        setTimeout(() => {
            window.open(`/students/${encodedStudentId}`, "_blank", "noopener,noreferrer");
        }, 1000); // Small delay prevents immediate redirection
        
    };


    const copyToClipboard = (text) => {
        if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
            navigator.clipboard.writeText(text)
                .then(() => message.success("Phone number copied!"))
                .catch(() => message.error("Failed to copy!"));
        } else {
            const textArea = document.createElement("textarea");
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand("copy");
            document.body.removeChild(textArea);
            message.success("Phone number copied!");
        }
    };



    return (
        <>
        <div className="w-auto pt-4 px-2 mt-14 darkmode">
            <BatchCards handleTabClick={handleTabClick} activeTab={activeTab}/>

            <div className="relative w-full h-full mt-2 shadow-md sm:rounded-lg border border-gray-100">
                <div className="w-full px-4 py-3 text flex justify-between font-semibold ">
                    <h1>All Batches</h1>
                    <div>
                        <button onClick={() =>  { setIsModalOpen(true); setSelectedBatch(null); }} type="button" className="focus:outline-none text-white bg-green-500 hover:bg-green-600 focus:ring-4 focus:ring-green-300 font-medium rounded-lg text-sm px-4 py-1.5">Create Batch +</button>
                    </div>
                </div>

                <div className="w-full grid grid-cols-5 grid-flow-row space-y-4 sm:space-y-0 items-center justify-between gap-x-8 px-4 pb-4">
                    <div className="grid col-span-5">
                        <div className="flex gap-x-4 h-auto flex-wrap justify-between items-center">
                            
                             <div className="lg:hidden mb-2">
                                <select
                                    value={activeTab}
                                    onChange={(e) => handleTabClick(e.target.value)}
                                    className="block w-auto px-4 py-1 text-sm border rounded-md bg-gray-100 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
                                >
                                <option value="running">Active</option>
                                <option value="scheduled">Scheduled</option>
                                <option value="hold">Hold</option>
                                <option value="endingsoon">Ending Soon</option>
                                <option value="completed">Completed</option>
                                <option value="cancelled">Cancelled</option>
                                </select>
                            </div>

                            {/* <div className="relative hidden lg:flex">
                                    <Badge count={batchData?.count ?? 0} overflowCount={999} size="small">
                                <button
                                    onClick={() => handleTabClick("Running")}
                                    className={`px-4 py-2 text-xs font-semibold rounded-sm transition-colors duration-200
                                        ${activeTab === "Running" ? 'bg-blue-300 text-black' : 'bg-gray-100 text-gray-700 hover:bg-blue-100'}`}
                                        >
                                    Active
                                </button>
                                    </Badge>
                                
                                <button
                                    onClick={() => handleTabClick("Upcoming")}
                                    className={`px-4 py-2 text-xs font-semibold rounded-sm transition-colors duration-200
                                        ${activeTab === "Upcoming" ? 'bg-blue-300 text-black' : 'bg-gray-100 text-gray-700 hover:bg-blue-100'}`}
                                    >
                                    Scheduled
                                </button>
                                
                                <button
                                    onClick={() => handleTabClick("Hold")}
                                    className={`px-4 py-2 text-xs font-semibold rounded-sm transition-colors duration-200
                                        ${activeTab === "Hold" ? 'bg-blue-300 text-black' : 'bg-gray-100 text-gray-700 hover:bg-blue-100'}`}
                                    >
                                    Hold
                                </button>
                                
                                <button
                                    onClick={() => handleTabClick("endingsoon")}
                                    className={`px-4 py-2 text-xs font-semibold rounded-sm transition-colors duration-200
                                        ${activeTab === "endingsoon" ? 'bg-blue-300 text-black' : 'bg-gray-100 text-gray-700 hover:bg-blue-100'}`}
                                    >
                                    Ending Soon
                                </button>
                                
                                <button
                                    onClick={() => handleTabClick("Completed")}
                                    className={`px-4 py-2 text-xs font-semibold rounded-sm transition-colors duration-200
                                        ${activeTab === "Completed" ? 'bg-blue-300 text-black' : 'bg-gray-100 text-gray-700 hover:bg-blue-100'}`}
                                    >
                                    Completed 
                                </button>
                                
                                <button
                                    onClick={() => handleTabClick("Cancelled")}
                                    className={`px-4 py-2 text-xs font-semibold rounded-sm transition-colors duration-200 
                                        ${activeTab === "Cancelled" ? 'bg-blue-300 text-black' : 'bg-gray-100 text-gray-700 hover:bg-blue-100'}`}
                                    >
                                    Cancelled
                                </button>
                                
                            </div> */}

                           <div className="relative hidden lg:flex ">
                                {["Running", "Scheduled", "Hold", "endingsoon", "Completed", "Cancelled"].map((tab) => {
                                    const isActive = activeTab === tab;
                                    const showCount = isActive ? batchData?.count : 0;

                                    return (
                                    <div key={tab} className="relative">
                                        <Badge
                                        count={showCount}
                                        overflowCount={999}
                                        size="small"
                                        offset={[2, -6]} // Adjust position of the badge
                                        >
                                        <button
                                            onClick={() => handleTabClick(tab)}
                                            className={`px-4 py-2 text-xs font-semibold rounded-sm transition-colors duration-200
                                            ${isActive ? 'bg-blue-300 text-black' : 'bg-gray-100 text-gray-700 hover:bg-blue-100'}`}
                                        >
                                            {tab === "endingsoon" ? "Ending Soon" : tab}
                                        </button>
                                        </Badge>
                                    </div>
                                    );
                                })}
                                </div>



                            <div className="grid col-span-1 justify-items-end">
                                <div className="flex gap-x-6">
                                    <label htmlFor="table-search" className="sr-only">Search</label>
                                        <SearchBar placeholder="Search for Batch"
                                            inputClassName="2xl:w-96 lg:w-96 md:w-72 h-8 block p-2 pr-10 text-xs text-gray-600 font-normal border border-gray-300 rounded-lg bg-gray-50 focus:ring-0 focus:border-blue-500"
                                            onSearch={(value) => {
                                                setSearchTerm(value);
                                                setCurrentPage(1);
                                            }}
                                        />
                                </div>
                            </div>

                        </div>
                    </div>
                </div>
                
                {/* {activeTab === 'tab1' && ( */}
                <div className={`overflow-hidden pb-2 relative ${loading ? "backdrop-blur-md opacity-50 pointer-events-none" : ""}`}>
                    <div className="w-full h-[38rem] overflow-y-auto rounded-lg pb-2">
                        <table className="w-full text-xs text-left text-gray-500">
                            <thead className="text-xs text-gray-700 uppercase bg-blue-50 sticky top-0 z-10">
                                <tr>
                                    <th scope="col" className="p-2">
                                        <div className="flex items-center">
                                            <input id="checkbox-all-search" type="checkbox" className="w-3 h-3 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-2"></input>
                                            <label htmlFor="checkbox-all-search" className="sr-only">checkbox</label>
                                        </div>
                                    </th>
                                    <th scope="col" className="px-3 py-3 md:px-2">
                                        S.No
                                    </th>
                                    <th scope="col" className="px-3 py-3 md:px-1">
                                        Batch Id
                                    </th>
                                    <th scope="col" className="px-3 py-3 md:px-1 cursor-pointer" onClick={toggleSortByStartTime}>
                                        Start Time 
                                    <span className="ml-1">
                                            <Tooltip title="Sort by Start Time" placement="top"> 
                                                {sortByTime ? "▲" : "▼"}
                                            </Tooltip>
                                    </span>
                                    </th>
                                    <th scope="col" className="px-3 py-3 md:px-1 cursor-pointer" onClick={toggleSortByStartDate}>
                                        Start Date
                                    <span className="ml-1">
                                            <Tooltip title="Sort by start Date" placement="top">
                                                {sortByStartDate ? "▲" : "▼"}
                                            </Tooltip>
                                    </span>
                                    </th>
                                    <th scope="col" className="px-3 py-3 md:px-1 cursor-pointer" onClick={toggleSortByEndDate}>
                                        End Date
                                        <span className="ml-1">
                                            <Tooltip title="Sort by End Date" placement="top">
                                                {sortByEndDate ? "▲" : "▼"}
                                            </Tooltip>
                                    </span>
                                    </th>
                                    <th scope="col" className="px-3 py-3 md:px-1">
                                        Course
                                        {/* <Tooltip title="Sort by Course" placement="top">
                                        <Dropdown menu={courseMenu} trigger={["click"]} >
                                            <Button type="text" icon={<FilterOutlined  />} />
                                        </Dropdown>
                                        </Tooltip> */}
                                    </th>
                                    <th scope="col" className="px-3 py-3 md:px-1">
                                        Trainer
                                        {/* <Tooltip title="Sort by Trainer" placement="top">
                                        <Dropdown  trigger={["click"]}>
                                            <Button type="text" icon={<FilterOutlined  style={{ color: sortByLanguage ? "blue" : "black" }} />} />
                                        </Dropdown>
                                        </Tooltip> */}
                                    </th>
                                    <th scope="col" className="px-3 py-3 md:px-1">
                                        Students
                                    </th>
                                    <th scope="col" className="px-3 py-3 md:px-1">
                                        Mode 
                                        <Tooltip title="Sort by Mode" placement="top">
                                        <span>
                                            <Dropdown menu={modeMenu} >
                                                <Button type="text" icon={<FilterOutlined  style={{ color: sortByMode ? "blue" : "black" }} className="w-3"/>} />
                                            </Dropdown>
                                        </span>
                                        </Tooltip>
                                    </th>
                                    <th scope="col" className="px-3 py-3 md:px-1">
                                        Language 
                                        <Tooltip title="Sort by Language" placement="top">
                                        <span>
                                            <Dropdown menu={languageMenu} >
                                                <Button type="text" icon={<FilterOutlined  style={{ color: sortByLanguage ? "blue" : "black" }} className="w-3"/>} />
                                            </Dropdown>
                                        </span>
                                        </Tooltip>
                                    </th>
                                    <th scope="col" className="px-3 py-3 md:px-1">
                                        Preferred Week
                                        <Tooltip title="Sort by Preferred Week" placement="top">
                                        <span>
                                            <Dropdown menu={preferredWeekMenu} >
                                                <Button type="text" icon={<FilterOutlined style={{ color: sortByPreferredWeek ? "blue" : "black" }} className="w-3"/>} />
                                            </Dropdown>
                                        </span>
                                        </Tooltip>
                                    </th>
                                    <th scope="col" className="px-3 py-3 md:px-1">
                                        Location
                                        <Tooltip title="Sort by Location" placement="top">
                                        <span>
                                            <Dropdown menu={locationMenu} >
                                                <Button type="text" icon={<FilterOutlined style={{ color: sortByLocation ? "blue" : "black" }} className="w-3"/>} />
                                            </Dropdown>
                                        </span>
                                        </Tooltip>
                                    </th>
                                    <th scope="col" className="px-3 py-3 md:px-1">
                                        Status
                                    </th>
                                    <th scope="col" className="px-3 py-3 md:px-1">
                                        Action
                                    </th>
                                    
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr>
                                        <td colSpan="100%" className="text-center py-4">
                                            <Spin size="large" />
                                        </td>
                                    </tr>
                                ) : sortedBatches.length > 0 ? (
                                    sortedBatches.map((item, index) => (
                                        <tr key={index} className="bg-white border-b border-gray-200 hover:bg-gray-50 scroll-smooth">
                                            <td scope="col" className="p-2">
                                                <div className="flex items-center">
                                                    <input id="checkbox-all-search" type="checkbox" className="w-3 h-3 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 focus:ring-2"></input>
                                                    <label htmlFor="checkbox-all-search" className="sr-only">checkbox</label>
                                                </div>
                                            </td>
                                            <td scope="row" className="px-3 py-2 md:px-2 font-medium text-gray-900 dark:text-white">
                                                {index + 1}
                                            </td>
                                            <td className="px-3 py-2 md:px-1 font-bold cursor-pointer" onClick={() => handleBatchClick(navigate,item.id)}>
                                                {item.batch_id} {item.batch_link && ( 
                                                    <Tooltip title={
                                                        <span overlayStyle={{ whiteSpace: "nowrap", maxWidth: 'none' }}>
                                                            Class Link - {item.batch_link}
                                                        </span>
                                                        }
                                                        >
                                                        <span>
                                                        <LinkOutlined style={{ color: "blue" }} />
                                                        </span>
                                                    </Tooltip>
                                                )}
                                            </td>
                                            <td className="px-3 py-2 md:px-1">
                                                {dayjs(`1970-01-01T${item.batch_time_data?.start_time}`).format("hh:mm A")}
                                                <span> - </span>
                                                {dayjs(`1970-01-01T${item.batch_time_data?.end_time}`).format("hh:mm A")}
                                            </td>
                                            <td className="px-3 py-2 md:px-1"> 
                                                {dayjs(item.start_date).format("DD/MM/YYYY")}
                                            </td>
                                            <td className="px-3 py-2 md:px-1"> 
                                                {dayjs(item.end_date).format("DD/MM/YYYY")}
                                            </td>
                                            <td className="px-3 py-2 md:px-1">{item.course_name}</td>

                                            <td className="px-3 py-2 md:px-1 font-bold cursor-pointer" onClick={() => handleTrainerClick(navigate,item.trainer)}>{item.trainer_name}</td>
                                            
                                            <td className="px-3 py-2 md:px-1 relative">
                                                {/* <Avatar.Group
                                                    max={{
                                                        count: 2,
                                                        style: {
                                                        color: "#f56a00",
                                                        backgroundColor: "#fde3cf",
                                                        height: "24px",
                                                        width: "24px",
                                                        },
                                                    }}
                                                    >
                                                    {item.student_name?.slice(0, 0).map((name, index) => (
                                                        <Avatar size={24} style={{ backgroundColor: "#87d068" }}>
                                                            {name[0]}
                                                        </Avatar>
                                                    ))}
                                                    {item.student_name?.map((name, index) => (
                                                        <Avatar key={index} size={24} style={{ display: "none" }}>
                                                        {name[0]}
                                                        </Avatar>
                                                    ))}
                                                </Avatar.Group> */}


                                                <Avatar.Group
                                                    max={{
                                                        count: 2,
                                                        style: {
                                                            color: "#f56a00",
                                                            backgroundColor: "#fde3cf",
                                                            height: "24px", // Match avatar size
                                                            width: "24px", // Match avatar size
                                                        }
                                                    }}
                                                    >
                                                    {item.student_name?.map((name, index) => (
                                                        <Tooltip key={index} title={name} placement="top">
                                                            <Avatar
                                                                size={24}
                                                                style={{ backgroundColor: "#87d068" }}
                                                            >
                                                                {name[0]} 
                                                            </Avatar>
                                                        </Tooltip>
                                                    ))}
                                                </Avatar.Group>

                                                <div className="relative inline-block">
                                                    <Button
                                                        disabled={item.status === "Cancelled" || item.status === "Completed"}
                                                        color="primary"
                                                        variant="filled"
                                                        className="ml-1 rounded-full"
                                                        size="small"
                                                        onClick={() => {
                                                            handleStudentDropdown(item.id, index);
                                                            fetchAvailableStudents(item.id);
                                                        }}
                                                        >
                                                        {addStudentDropdown === index ? "-" : "+"}
                                                    </Button>

                                                    {addStudentDropdown === index && (
                                                        <div className="absolute left-full top-0 ml-2 bg-white border rounded shadow-lg p-2 z-50 flex">
                                                            <Select
                                                                showSearch
                                                                mode="multiple"
                                                                size="small"
                                                                style={{ width: 250, whiteSpace: "normal" }}
                                                                onChange={(values) => handleSelectChange(item.id, values)}
                                                                placeholder="Select a student"
                                                                options={students[item.id] ? students[item.id].map(student => ({
                                                                    label: (
                                                                        <div style={{ whiteSpace: "normal", wordWrap: "break-word", overflowWrap: "break-word" }}>
                                                                            {student.name} - {student.phone}
                                                                        </div>
                                                                    ),
                                                                    title: `${student.name} - ${student.phone}`,
                                                                    value: student.studentid,
                                                                    phone:  student.phone,
                                                                    dataName: student.name.toLowerCase(), 
                                                                    dataPhone: student.phone.toLowerCase(),
                                                                })) : []}
                                                                filterOption={(input, option) =>
                                                                    option.dataName.includes(input.toLowerCase()) ||
                                                                    option.dataPhone.includes(input.toLowerCase())
                                                                }
                                                                optionRender={(option) => (
                                                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%" }}>
                                                                        {/* Left-aligned student name & phone */}
                                                                        <span style={{ flex: 1 }}>{option.data.label}</span>
                                                                
                                                                        {/* Right-aligned icons */}
                                                                        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                                                                        <Tooltip title="Copy Phone Number">
                                                                            <span>
                                                                                <CopyOutlined
                                                                                    style={{ cursor: "pointer", color: "#1890ff" }}
                                                                                    onClick={(e) => {
                                                                                        e.stopPropagation();
                                                                                        copyToClipboard(option.data.phone);
                                                                                    }}
                                                                                />
                                                                            </span>
                                                                        </Tooltip>

                                                                        <Tooltip title="Open Student Info">
                                                                            <span>
                                                                                <RightOutlined
                                                                                    style={{ cursor: "pointer", color: "blue" }}
                                                                                    onClick={(e) => {
                                                                                        handleStudentClickOnSelect(e, option.data.value);
                                                                                    }}
                                                                                />
                                                                            </span>
                                                                        </Tooltip>

                                                                        </div>
                                                                    </div>
                                                                )}
                                                            />

                                                            <Button variant="solid" color="green" className="ml-1" size="small" onClick={() => { addStudents(item.id); setAddStudentDropdown(false); }}>
                                                                Add
                                                            </Button>
                                                        </div>
                                                    )}
                                                </div>
                                            </td>
                                            <td className="px-3 py-2 md:px-1">
                                                <Tag bordered={false} color={item.mode === "Offline" ? "green" : item.mode === "Online" ? "red" : "geekblue"}>
                                                    {item.mode}
                                                </Tag>
                                            </td>

                                            <td className="px-3 py-2 md:px-1">
                                                <Tag bordered={false} color={item.language === "Hindi" ? "green" : item.language === "English" ? "volcano" : "blue"}>
                                                    {item.language}
                                                </Tag>
                                            </td>

                                            <td className="px-3 py-2 md:px-1">
                                                <Tag bordered={false} color={item.preferred_week === "Weekdays" ? "cyan" : item.preferred_week === "Weekends" ? "gold" : "geekblue" }>
                                                    {item.preferred_week}
                                                </Tag>
                                            </td>

                                            <td className="px-3 py-2 md:px-1">
                                                <Tag bordered={false} color={item.batch_location === "saket" ? "blue" : item.batch_location === "Laxmi Nagar" ? "magenta" : "geekblue"}>
                                                    {item.batch_location}
                                                </Tag>
                                            </td>

                                            <td className="px-3 py-2 md:px-1">
                                                <Dropdown
                                                    menu={{
                                                        items: ["Running", "Completed", "Hold", "Cancelled"]
                                                            .filter((status) => !(item.status === "Running" && status === "Running" || item.status === "Hold" && status === "Hold"))
                                                            .map((status) => ({
                                                                key: status,
                                                                label: status,
                                                            })),
                                                        onClick: ({ key }) => onChangeStatus(item.id, key),
                                                    }}
                                                    >
                                                    <a onClick={(e) => e.preventDefault()}>
                                                        <Tag color={item.status === "Running" ? "green" : item.status === "Upcoming" ? "lime" : item.status === "Completed" ? "geekblue" : item.status === "Hold" ? "volcano" : "red"}>
                                                            {item.status} <span><DownOutlined /></span>
                                                        </Tag>
                                                    </a>
                                                </Dropdown>
                                            </td>

                                            <td>
                                                <Button
                                                    color="primary"
                                                    variant="filled"
                                                    className="rounded-lg w-auto pl-3 pr-3 py-0 my-1 mr-1"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleEditClick(item);
                                                        setIsModalOpen(true);
                                                    }}
                                                    >
                                                    <EditOutlined />
                                                </Button>

                                                <Popconfirm
                                                    title="Delete the Batch"
                                                    description="Are you sure you want to delete this Batch?"
                                                    onConfirm={() => confirm(item.id)}
                                                    onCancel={cancel}
                                                    okText="Yes"
                                                    cancelText="No"
                                                    >
                                                    <Button
                                                        color="danger"
                                                        variant="filled"
                                                        className="rounded-lg w-auto px-3"
                                                        onClick={(e) => e.stopPropagation()}
                                                        >
                                                        <DeleteOutlined />
                                                    </Button>
                                                </Popconfirm>
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan="100%" className="text-center py-4 text-gray-500">
                                            <Empty description="No Batches found" />
                                        </td>
                                    </tr>
                                )}
                            </tbody>

                        </table>
                    </div>

                    <div className="flex justify-center items-center mt-0 py-2 bg-blue-50">
                    <Pagination
                        size="small"
                            current={currentPage}
                            total={batchData?.count || 0}
                            pageSize={pageSize} // example: 30
                            onChange={(page) => setCurrentPage(page)}
                            showSizeChanger={false}    // hide page size select
                            showQuickJumper={false}    // hide quick jump input
                        />
                    </div>

                {/* {activeTab === "available_batches" && (
                    <AvailableBatches/>
                )} */}

                </div>
                {/* )} */}
            </div>

            <CreateBatchForm isOpen={isModalOpen} selectedBatchData={selectedBatch|| {}}  onClose={() => setIsModalOpen(false)} />

        </div>


        {/* Table for available trainers  */}
        <div>
            <AvailableBatches/>
        </div>

   </>
    )
}


export default Batches;