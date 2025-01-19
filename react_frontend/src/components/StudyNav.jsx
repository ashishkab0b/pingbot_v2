// StudyNav.js
import React from 'react';
import { Link as RouterLink, useParams, useMatch } from 'react-router-dom';
import { Tabs, Tab } from '@mui/material';

function StudyNav() {
  const { studyId } = useParams();

  // Define your navigation items
  const navItems = [
    { label: 'Study Overview', path: `/studies/${studyId}` },
    { label: 'Ping Templates', path: `/studies/${studyId}/ping_templates` },
    { label: 'Pings', path: `/studies/${studyId}/pings` },
    { label: 'Participants', path: `/studies/${studyId}/participants` },
    { label: 'Users', path: `/studies/${studyId}/users` },  
  ];

  // Use useMatch to check for route matches
  const matchStudyOverview = useMatch({ path: `/studies/${studyId}`, end: true });
  const matchPingTemplates = useMatch({ path: `/studies/${studyId}/ping_templates/*` });
  const matchPings = useMatch({ path: `/studies/${studyId}/pings/*` });
  const matchParticipants = useMatch({ path: `/studies/${studyId}/participants/*` });
  const matchUsers = useMatch({ path: `/studies/${studyId}/users/*` });

  // Determine the current active tab index
  let currentTab = false; // Default to no tab selected

  if (matchStudyOverview) {
    currentTab = 0;
  } else if (matchPingTemplates) {
    currentTab = 1;
  } else if (matchPings) {
    currentTab = 2;
  } else if (matchParticipants) {
    currentTab = 3;
  } else if (matchUsers) {
    currentTab = 4;
  }


  return (
    <Tabs
      value={currentTab}
      indicatorColor="primary"
      textColor="primary"
      variant="scrollable"
      scrollButtons="auto"
      aria-label="Study Navigation Tabs"
      sx={{ marginBottom: 2 }}
    >
      {navItems.map((item, index) => (
        <Tab
          key={index}
          label={item.label}
          component={RouterLink}
          to={item.path}
        />
      ))}
    </Tabs>
  );
}

export default StudyNav;