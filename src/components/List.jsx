const List = ({ listTitles }) => {
    return (
        <div className="list">
            {
                listTitles.map((clustor) => (
                    <div className="p-6 max-w-sm bg-white rounded-lg border border-gray-200 shadow-md dark:bg-gray-800 dark:border-gray-700" key={clustor.address}>
                    <svg className="mb-2 w-10 h-10 text-gray-500 dark:text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,20a9,9,0,1,1,9-9A9,9,0,0,1,12,21ZM14,7V6a1,1,0,0,0-2,0V7H11V6A1,1,0,0,0,9,6V7H8A1,1,0,0,0,8,9H9v6H8a1,1,0,0,0,0,2H9v1a1,1,0,0,0,2,0V17h1v1a1,1,0,0,0,2,0V17a3,3,0,0,0,3-3,3,3,0,0,0-.77-2A3,3,0,0,0,17,10,3,3,0,0,0,14,7Zm0,8H11V13h3a1,1,0,0,1,0,2Zm0-4H11V9h3a1,1,0,0,1,0,2Z"/></svg>
                    <svg className="mb-2 w-10 h-10 text-gray-500 dark:text-gray-400" xmlns="http://www.w3.org/2000/svg" data-name="Layer 1" viewBox="0 0 128 128"><path d="M93.94 42.63H13.78l20.28-20.22h80.16L93.94 42.63zM93.94 105.59H13.78l20.28-20.21h80.16M34.06 74.11h80.16L93.94 53.89H13.78"/></svg>
                        <a href="href={`/clustors/${clustor.address}/`}">
                            <h5 className="mb-2 text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">{ clustor.cname }</h5>
                        </a>
                        <p className="mb-3 font-normal text-gray-500 dark:text-gray-400">Go to this step by step guideline process on how to certify for your weekly benefits:</p>
                        <a href="#" className="inline-flex items-center text-blue-600 hover:underline">
                            See our guideline
                            <svg className="ml-2 w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z"></path><path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z"></path></svg>
                        </a>
                    </div>
                    ))
                    
            } 
        </div>
    );
};

export default List;
