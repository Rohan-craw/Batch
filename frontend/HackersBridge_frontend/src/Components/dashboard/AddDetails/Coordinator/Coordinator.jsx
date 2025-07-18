import { useEffect, useState } from "react"
import axios from "axios";
import BASE_URL from "../../../../ip/Ip";
import { Button, message, Popconfirm, Switch, Empty, Spin } from 'antd';
import { EditOutlined, DeleteOutlined, CheckOutlined, CloseOutlined } from '@ant-design/icons';
import AddCoordinatorForm from "./AddCoordinatorForm";
import { useCoordinatorForm } from "./CoordinatorContext";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../AuthContext/AuthContext";
import { handleCoordinatorClick } from "../../../Navigations/Navigations";
import Tags from "../../Tags/Tags";






const Coordinators = () => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedCoordinator, setSelectedCoordinator] = useState(); 
    const [isDeleted, setIsDeleted] = useState(false);
    const [coordinatorStatuses, setCoordinatorStatuses] = useState({}); // Store status per trainer

    const { coordinatorData, loading, setLoading, setCoordinatorData, fetchCoordinators } = useCoordinatorForm();
    
    const navigate = useNavigate();

    // Fetch batches afer deletion or modal open
    useEffect(() => {
        fetchCoordinators();
        setIsDeleted(false);

        if (coordinatorData) {
            // Ensure trainerData.all_data.trainers exists and is an array
            const coordinatorArray = Array.isArray(coordinatorData)
                ? coordinatorData
                : [];

            // Set a timeout to wait 2 seconds before initializing statuses
            const timer = setTimeout(() => {
                const initialStatuses = {};
                coordinatorArray.forEach((coordinator) => {
                    initialStatuses[coordinator.id] = coordinator.status === "Active"; 
                });

                setCoordinatorStatuses(initialStatuses); 
            }, 100);

            // Cleanup function to clear the timer if the component unmounts
            return () => clearTimeout(timer);
        }

    },[isDeleted, selectedCoordinator, isModalOpen, coordinatorData])


     // Function to handle Edit button click 
     const handleEditClick = (coordinator) => {
        setSelectedCoordinator(coordinator);
        setIsModalOpen(true);
        setIsDeleted(false);
    };

     // Delete Function 
     const handleDelete = async (coordinatorId) => {
        if (!coordinatorId) return;

        try {
            const response = await axios.delete(`${BASE_URL}/api/coordinators/delete/${coordinatorId}/`, 
                { headers: { 'Content-Type': 'application/json' },
                withCredentials : true
            }
            );

            if (response.status === 204) {
                // Make sure coursesData is an array before filtering
                if (Array.isArray(coordinatorData)) {
                    setCoordinatorData(prevCoordinator => prevCoordinator.filter(coordinator => coordinator.id !== coordinatorId));
                } else {
                    console.error('coordinatordata is not an array');
                }
            }
        }catch (error) {
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
      const confirm = (coordinatorId) => {
        handleDelete(coordinatorId);
        message.success('Coordinator Deleted Successfully');
    };

    const cancel = () => {
        message.error('Coordinator Deletion Cancelled');
    };
    


    // Handle Toggle of coordinator active and inactive 
    const handleToggle = async (checked, coordinatorId, coordinatorEmail) => {
        const newStatus = checked ? "Active" : "Inactive";
        
        // Optimistically update UI before API call
        setCoordinatorStatuses((prev) => ({ ...prev, [coordinatorId]: checked }));
    
        try {
            await axios.put(`${BASE_URL}/api/coordinators/edit/${coordinatorId}/`, 
                { status: newStatus, email: coordinatorEmail },
                { headers: { 'Content-Type': 'application/json' },
                withCredentials : true
            }
            );
            message.success(`Coordinator status updated to ${newStatus}`);
        } catch (error) {
            message.error("Failed to update status");
            // Revert UI if API fails
            setCoordinatorStatuses((prev) => ({ ...prev, [coordinatorId]: !checked }));
        }
    };



    return (
        <>
            <div className="w-auto pt-4 px-2 mt-10 ">
                <div className="relative w-full h-full shadow-md sm:rounded-lg  border border-gray-50 dark:border dark:border-gray-600">
                    <div className="w-full px-4 py-3 text flex justify-between font-semibold ">
                        <h1>All Coordinators</h1>
                            <div>
                                <button onClick={() =>  { setIsModalOpen(true); setSelectedCoordinator(null); }} type="button" className="focus:outline-none text-white bg-green-500 hover:bg-green-600 focus:ring-4 focus:ring-green-300 font-medium rounded-lg text-sm px-4 py-1.5 dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800">Add Coordinator +</button>
                            </div>
                    </div>

                    <div className={`overflow-hidden pb-2 relative ${loading ? "backdrop-blur-md opacity-50 pointer-events-none" : ""}`}>
                        <div className="w-full h-[30rem] overflow-y-auto dark:border-gray-700 rounded-lg pb-2">
                    <table className="w-full text-xs text-left text-gray-500 dark:text-gray-400 ">
                        <thead className="text-xs text-gray-700 uppercase bg-blue-50 dark:bg-gray-700 dark:text-gray-400 sticky top-0">
                            <tr>
                                {/* <th scope="col" className="p-4">
                                    <div className="flex items-center">
                                        <input id="checkbox-all-search" type="checkbox" className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 dark:focus:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"></input>
                                        <label htmlFor="checkbox-all-search" className="sr-only">checkbox</label>
                                    </div>
                                </th> */}
                                <th scope="col" className="px-3 py-3 md:px-1">
                                    S.No
                                </th>
                                <th scope="col" className="px-3 py-3 md:px-1">
                                    Coordinator ID
                                </th>
                                <th scope="col" className="px-3 py-3 md:px-1">
                                    Name
                                </th>
                                <th scope="col" className="px-3 py-3 md:px-1">
                                    Phone Number
                                </th>
                                <th scope="col" className="px-3 py-3 md:px-1">
                                    Email Address
                                </th>
                                <th scope="col" className="px-3 py-3 md:px-1">
                                    Week Off
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
                    
                        ) : coordinatorData &&  Array.isArray(coordinatorData) && coordinatorData.length > 0 ? (
                            coordinatorData.map((item, index) => (    
                                <tr key={item.id} className="bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600 scroll-smooth">
                                <td scope="row" className="px-3 py-2 md:px-2 font-medium text-gray-900  dark:text-white">
                                    {index + 1}
                                </td>
                                <td className="px-3 py-2 md:px-1 font-bold cursor-pointer" onClick={() => handleCoordinatorClick(navigate,item.id)}>
                                    {item.coordinator_id}
                                </td>
                                <td className="px-3 py-2 md:px-1 font-bold cursor-pointer" onClick={() => handleCoordinatorClick(navigate,item.id)}>
                                    {item.name}
                                </td>
                                <td className="px-3 py-2 md:px-1">
                                    {item.phone}
                                </td>
                                <td className="px-3 py-2 md:px-1">
                                    {item.email}
                                </td>
                                <td className="px-3 py-2 md:px-1">
                                    {item.weekoff}
                                </td>
                                <td className="px-3 py-2 md:px-1">
                                    <Switch
                                        size="small"
                                        checkedChildren={<CheckOutlined />}
                                        unCheckedChildren={<CloseOutlined />}
                                        checked={coordinatorStatuses[item.id] || false} // Get correct status per trainer
                                        onChange={(checked) => handleToggle(checked, item.id, item.email)}
                                        style={{
                                            backgroundColor: coordinatorStatuses[item.id] ? "#38b000" : "gray", // Change color when checked
                                          }}
                                    /> 
                                </td>
                                <td > <Button 
                                        color="primary" 
                                        variant="filled" 
                                        className="rounded-lg w-auto pl-3 pr-3 py-0 my-1 mr-1"
                                        onClick={(e) => {
                                            e.stopPropagation(); // Prevent the click from bubbling to the <td> click handler
                                            handleEditClick(item);  // Open the form with selected course data
                                            setIsModalOpen(true);   // Open the modal
                                        }}
                                    >
                                        <EditOutlined />
                                    </Button>
                                    <Popconfirm
                                        title="Delete the Coordinator"
                                        description="Are you sure you want to delete this Coordinator?"
                                        onConfirm={() => confirm(item.id)}
                                        onCancel={cancel}
                                        okText="Yes"
                                        cancelText="No"
                                    >
                                        <Button 
                                            color="danger" 
                                            variant="filled" 
                                            className="rounded-lg w-auto px-3"
                                            onClick={(e) => e.stopPropagation()} // Prevent the click from triggering the Edit button
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
                                    <Empty description="No Coordinators found" />
                                </td>
                            </tr>
                        )}
                        </tbody>
                    </table>
                    </div>

                    </div>
                </div>

                <>
                    <Tags />
                </>

            <AddCoordinatorForm isOpen={isModalOpen} coordinatorData={selectedCoordinator|| {}} onClose={() => setIsModalOpen(false)} />

            </div>  

   </>
    )
}


export default Coordinators;