
import React from 'react';
import { Link, useParams } from 'react-router-dom';

function StudyNav() {
  const { studyId } = useParams();

  return (
    <nav>
      <Link to={`/studies/${studyId}`}>Study Overview</Link> | 
      <Link to={`/studies/${studyId}/ping_templates`}>Ping Templates</Link> | 
      <Link to={`/studies/${studyId}/pings`}>Pings</Link> | 
      <Link to={`/studies/${studyId}/participants`}>Participants</Link> | 
    </nav>
  );
}

export default StudyNav;