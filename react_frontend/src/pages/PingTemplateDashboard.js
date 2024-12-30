import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useForm, FormProvider, Controller } from 'react-hook-form';
import axios from '../api/axios'; 
import StudyNav from '../components/StudyNav';
import { useStudy } from '../context/StudyContext';
import PingScheduleForm from '../components/PingScheduleForm';
import VariableAutoCompleteTextarea from '../components/VariableAutoCompleteTextarea';
import DataTable from '../components/DataTable';
import DeleteIcon from '@mui/icons-material/Delete';
import { IconButton, Tooltip } from '@mui/material';


function PingTemplateDashboard() {


  const [message, setMessage] = useState('');
  const [url, setUrl] = useState('');

// Variables for each field
const urlVariables = [
  '<PING_ID>', 
  '<REMINDER_TIME>', 
  '<SCHEDULED_TIME>', 
  '<EXPIRE_TIME>', 
  '<DAY_NUM>', 
  '<PING_TEMPLATE_ID>', 
  '<PING_TEMPLATE_NAME>', 
  '<STUDY_ID>', 
  '<STUDY_PUBLIC_NAME>', 
  '<STUDY_INTERNAL_NAME>', 
  '<STUDY_CONTACT_MSG>', 
  '<PID>',
  '<ENROLLMENT_ID>', 
  '<ENROLLMENT_START_DATE>', 
  '<PR_COMPLETED>'
];
  const messageOnlyVariables = ['<URL>'];
  const messageVariables = [...urlVariables, ...messageOnlyVariables];

  
  
  // -----------------------------------------
  // URL param, state for listing
  // -----------------------------------------
  const { studyId } = useParams();
  const study = useStudy();
  const [pingTemplates, setPingTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [page, setPage] = useState(1);
  const [perPage] = useState(5);
  const [totalPages, setTotalPages] = useState(1);
  const [showCreateForm, setShowCreateForm] = useState(false);

  // -----------------------------------------
  // React Hook Form: Use "FormProvider" to share context
  // -----------------------------------------
  const methods = useForm({
    defaultValues: {
      name: '',
      message: '',
      url: '',
      url_text: 'Click here to take the survey',
      reminderEnabled: false,
      reminderHours: 0,
      reminderMinutes: 0,
      expireEnabled: false,
      expireHours: 0,
      expireMinutes: 0,

      // Fields for scheduling
      studyLength: 7,
      scheduleMode: 'everyDay',

      everyDayPingsCount: 1,
      everyDayPings: [
        { beginTime: '09:00', endTime: '17:00', nextDay: false }
      ],
      perDaySchedule: []
    }
  });

  const { handleSubmit, reset } = methods;

  // -----------------------------------------
  // Fetch existing Ping Templates
  // -----------------------------------------
  useEffect(() => {
    if (studyId) {
      fetchPingTemplates(studyId, page, perPage);
    }
    // eslint-disable-next-line
  }, [studyId, page]);

  const fetchPingTemplates = async (studyIdParam, currentPage, itemsPerPage) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        `/studies/${studyIdParam}/ping_templates?page=${currentPage}&per_page=${itemsPerPage}`
      );
      const { data, meta } = response.data;
      setPingTemplates(data);
      setPage(meta.page);
      setTotalPages(meta.pages);
    } catch (err) {
      console.error(err);
      setError('Error fetching ping templates');
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------------------
  // Delete a Ping Template
  // -----------------------------------------
  const deletePingTemplate = async (templateId) => {
    if (!window.confirm("Are you sure you want to delete this ping template?")) return;
  
    try {
      await axios.delete(`/studies/${studyId}/ping_templates/${templateId}`);
      alert("Ping template deleted successfully.");
      fetchPingTemplates(studyId, page, perPage); // Refresh the list after deletion
    } catch (err) {
      console.error(err);
      alert("Error deleting ping template.");
    }
  };

  // -----------------------------------------
  // Build schedule JSON for submission
  // -----------------------------------------
  const buildScheduleJSON = (data) => {
    if (data.scheduleMode === 'everyDay') {
      const totalDays = data.studyLength + 1;
      const scheduleArray = [];
      const startingDayNum = 1;
      for (let day = startingDayNum; day < totalDays; day++) {
        data.everyDayPings.forEach((ping) => {
          scheduleArray.push({
            begin_day_num: day,
            begin_time: ping.beginTime,
            end_day_num: ping.nextDay ? day + 1 : day,
            end_time: ping.endTime
          });
        });
      }
      return scheduleArray;
    } else {
      // perDay mode
      const result = [];
      data.perDaySchedule.forEach((dayObj) => {
        if (!dayObj.active) return;
        dayObj.pings.forEach((ping) => {
          result.push({
            begin_day_num: dayObj.day,
            begin_time: ping.beginTime,
            end_day_num: ping.nextDay ? dayObj.day + 1 : dayObj.day,
            end_time: ping.endTime
          });
        });
      });
      return result;
    }
  };

  // -----------------------------------------
  // Build reminder/expire strings
  // -----------------------------------------
  const buildLatencyString = (hours, minutes) => {
    const h = parseInt(hours, 10);
    const m = parseInt(minutes, 10);
    if (h === 0 && m === 0) return null;
    let parts = [];
    if (h > 0) parts.push(`${h} hour${h > 1 ? 's' : ''}`);
    if (m > 0) parts.push(`${m} minute${m > 1 ? 's' : ''}`);
    return parts.join(' ');
  };

  // -----------------------------------------
  // On Submit
  // -----------------------------------------
  const onSubmit = async (formData) => {
    try {
      const scheduleJSON = buildScheduleJSON(formData);
      const reminderLatency = formData.reminderEnabled
        ? buildLatencyString(formData.reminderHours, formData.reminderMinutes)
        : null;
      const expireLatency = formData.expireEnabled
        ? buildLatencyString(formData.expireHours, formData.expireMinutes)
        : null;

      await axios.post(`/studies/${studyId}/ping_templates`, {
        name: formData.name,
        message: formData.message,
        url: formData.url,
        url_text: formData.url_text,
        reminder_latency: reminderLatency,
        expire_latency: expireLatency,
        schedule: scheduleJSON
      });

      reset();
      setShowCreateForm(false);
      fetchPingTemplates(studyId, page, perPage);
    } catch (err) {
      console.error(err);
      setError('Error creating ping template');
    }
  };

  // -----------------------------------------
  // Pagination
  // -----------------------------------------
  const handlePreviousPage = () => {
    if (page > 1) setPage((prev) => prev - 1);
  };
  const handleNextPage = () => {
    if (page < totalPages) setPage((prev) => prev + 1);
  };

  if (!studyId) {
    return <div>Error: Missing studyId in the URL.</div>;
  }

  return (
    <div style={{ margin: '2rem' }}>

      <h1>Study: {study.internal_name}</h1>
      <StudyNav />
      {/* <h1>Ping Templates for {study?.internal_name || 'Loading...'}</h1> */}

      <button
        style={{ marginBottom: '1rem' }}
        onClick={() => setShowCreateForm(!showCreateForm)}
      >
        {showCreateForm ? 'Cancel' : 'Create New Ping Template'}
      </button>

      {showCreateForm && (
        <section style={{ marginBottom: '2rem' }}>
          <h2>Create a New Ping Template</h2>

          {/* Provide form context to children */}
          <FormProvider {...methods}>
            <form onSubmit={handleSubmit(onSubmit)} style={{ maxWidth: '600px' }}>
              {/* NAME */}
              <div style={{ marginBottom: '1rem' }}>
                <label>Name (required)</label>
                <br />
                <input
                  type="text"
                  style={{ width: '100%' }}
                  {...methods.register('name', { required: 'Name is required' })}
                />
                {methods.formState.errors.name && (
                  <p style={{ color: 'red' }}>
                    {methods.formState.errors.name.message}
                  </p>
                )}
              </div>

              {/* URL with autocomplete */}
              <div style={{ marginBottom: '1rem' }}>
              <label>URL (optional)</label>
              <Controller
                name="url"
                control={methods.control}
                render={({ field }) => (
                  <VariableAutoCompleteTextarea
                    value={url}
                    onChange={(value) => {
                      setUrl(value);
                      field.onChange(value); // Ensure React Hook Form updates the value
                    }}
                    variableOptions={urlVariables}
                  />
                )}
              />
            </div>

            {/* URL TEXT */}
            {methods.watch('url') && (
              <div style={{ marginBottom: '1rem' }}>
                <label>URL Text (required with URL)</label>
                <br />
                <input
                  type="text"
                  style={{ width: '100%' }}
                  {...methods.register('url_text')}
                />
                {methods.formState.errors.url_text && (
                  <p style={{ color: 'red' }}>
                    {methods.formState.errors.url_text.message}
                  </p>
                )}
              </div>
            )}

            {/* MESSAGE with autocomplete */}
            <div style={{ marginBottom: '1rem' }}>
              <label>Message (required)</label>
              <Controller
                name="message"
                control={methods.control}
                rules={{ required: 'Message is required' }}
                render={({ field }) => (
                  <VariableAutoCompleteTextarea
                    value={field.value} // Use the value from React Hook Form
                    onChange={(value) => {
                      setMessage(value); // Update local state
                      field.onChange(value); // Notify React Hook Form
                    }}
                    variableOptions={messageVariables}
                  />
                )}
              />
              {methods.formState.errors.message && (
                <p style={{ color: 'red' }}>
                  {methods.formState.errors.message.message}
                </p>
              )}
            </div>
            

              {/* REMINDER CHECKBOX */}
              <div style={{ marginBottom: '1rem' }}>
                <label>
                  <input type="checkbox" {...methods.register('reminderEnabled')} />
                  Enable Reminder
                </label>
                {methods.watch('reminderEnabled') && (
                  <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                    <div>
                      <label>Hours</label>
                      <input
                        type="number"
                        min="0"
                        style={{ width: '60px' }}
                        {...methods.register('reminderHours')}
                      />
                    </div>
                    <div>
                      <label>Minutes</label>
                      <input
                        type="number"
                        min="0"
                        max="59"
                        style={{ width: '60px' }}
                        {...methods.register('reminderMinutes')}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* EXPIRE CHECKBOX */}
              <div style={{ marginBottom: '1rem' }}>
                <label>
                  <input type="checkbox" {...methods.register('expireEnabled')} />
                  Enable Expire
                </label>
                {methods.watch('expireEnabled') && (
                  <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                    <div>
                      <label>Hours</label>
                      <input
                        type="number"
                        min="0"
                        style={{ width: '60px' }}
                        {...methods.register('expireHours')}
                      />
                    </div>
                    <div>
                      <label>Minutes</label>
                      <input
                        type="number"
                        min="0"
                        max="59"
                        style={{ width: '60px' }}
                        {...methods.register('expireMinutes')}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* STUDY LENGTH */}
              <div style={{ marginBottom: '1rem' }}>
                <label>Study Length (in days)</label>
                <input
                  type="number"
                  style={{ marginLeft: '0.5rem', width: '80px' }}
                  {...methods.register('studyLength', { min: 0 })}
                />
              </div>

              {/* SCHEDULE FORM */}
              <PingScheduleForm />

              <button type="submit">Create Ping Template</button>
            </form>
          </FormProvider>
        </section>
      )}

      {/* List existing Ping Templates */}
      <section>
        {/* <h2>Ping Templates</h2> */}

        <DataTable
          data={pingTemplates.map((pt) => ({
            // Update data keys to match the 'key' in columns
            id: pt.id,
            name: pt.name,
            message: pt.message,
            url: pt.url,
            reminderLatency: pt.reminder_latency,
            expireLatency: pt.expire_latency,
            schedule: JSON.stringify(pt.schedule),
          }))}
          columns={[
            { label: 'ID', key: 'id' },
            { label: 'Name', key: 'name' },
            { label: 'Message', key: 'message' },
            { label: 'URL', key: 'url' },
            { label: 'Reminder Latency', key: 'reminderLatency' },
            { label: 'Expire Latency', key: 'expireLatency' },
            { label: 'Schedule', key: 'schedule' },
          ]}
          loading={loading}
          error={error}
          currentPage={page}
          totalPages={totalPages}
          onPreviousPage={handlePreviousPage}
          onNextPage={handleNextPage}
          actionsColumn={(row) => (
            
              <Tooltip title="Delete Ping Template">
              <IconButton
                color="error"
                onClick={(e) => {
                  e.stopPropagation();
                  deletePingTemplate(row.id);
                }}
              >
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          )}
        />
      </section>
    </div>
  );
}

export default PingTemplateDashboard;