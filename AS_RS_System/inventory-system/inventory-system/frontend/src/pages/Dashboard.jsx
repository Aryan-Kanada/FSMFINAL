import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import BoxesTab from '../components/BoxesTab';
import ItemsTab from '../components/ItemsTab';
import SubCompartmentsTab from '../components/SubCompartmentsTab';
import TransactionsTab from '../components/TransactionsTab';
import OperationsTab from '../components/OperationsTab';
import { ToastContainer, Flip } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function Dashboard() {
  const [activeTab, setActiveTab] = useState('boxes');
  const [isTabChanging, setIsTabChanging] = useState(false);

  // Tab transition variants
  const tabContentVariants = {
    hidden: { opacity: 0, x: 20 },
    visible: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 }
  };

  // Handle tab change with animation
  const handleTabChange = (tab) => {
    if (tab !== activeTab) {
      setIsTabChanging(true);
      setTimeout(() => {
        setActiveTab(tab);
        setIsTabChanging(false);
      }, 300);
    }
  };

  // Render tab content with transitions
  const renderTabContent = () => {
    return (
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial="hidden"
          animate="visible"
          exit="exit"
          variants={tabContentVariants}
          transition={{ duration: 0.3 }}
          className="tab-content-inner"
        >
          {(() => {
            switch (activeTab) {
              case 'boxes':
                return <BoxesTab />;
              case 'items':
                return <ItemsTab />;
              case 'subcompartments':
                return <SubCompartmentsTab />;
              case 'transactions':
                return <TransactionsTab />;
              case 'operations':
                return <OperationsTab />;
              default:
                return <BoxesTab />;
            }
          })()}
        </motion.div>
      </AnimatePresence>
    );
  };

  // Create ripple effect for tab buttons
  const createRipple = (event) => {
    const button = event.currentTarget;
    
    const circle = document.createElement("span");
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - button.getBoundingClientRect().left - radius}px`;
    circle.style.top = `${event.clientY - button.getBoundingClientRect().top - radius}px`;
    circle.classList.add("ripple");
    
    const ripple = button.getElementsByClassName("ripple")[0];
    
    if (ripple) {
      ripple.remove();
    }
    
    button.appendChild(circle);
  };

  return (
    <div className="dashboard">
      <motion.header 
        className="dashboard-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <h1>Inventory Management System</h1>
      </motion.header>
      
      <motion.div 
        className="tabs"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.4 }}
      >
        <button 
          className={activeTab === 'boxes' ? 'active' : ''} 
          onClick={(e) => {
            createRipple(e);
            handleTabChange('boxes');
          }}
        >
          Boxes
        </button>
        <button 
          className={activeTab === 'items' ? 'active' : ''} 
          onClick={(e) => {
            createRipple(e);
            handleTabChange('items');
          }}
        >
          Items
        </button>
        <button 
          className={activeTab === 'subcompartments' ? 'active' : ''} 
          onClick={(e) => {
            createRipple(e);
            handleTabChange('subcompartments');
          }}
        >
          Sub Compartments
        </button>
        <button 
          className={activeTab === 'transactions' ? 'active' : ''} 
          onClick={(e) => {
            createRipple(e);
            handleTabChange('transactions');
          }}
        >
          Transactions
        </button>
        <button 
          className={activeTab === 'operations' ? 'active' : ''} 
          onClick={(e) => {
            createRipple(e);
            handleTabChange('operations');
          }}
        >
          Operations
        </button>
      </motion.div>
      
      <motion.div 
        className="tab-content"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        {renderTabContent()}
      </motion.div>
      
      <ToastContainer 
        position="bottom-right"
        autoClose={4000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
        transition={Flip}
      />
    </div>
  );
}

export default Dashboard;
