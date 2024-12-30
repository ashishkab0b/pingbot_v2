// PingTemplateDashboard.js

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
import {
  IconButton,
  Tooltip,
  Button,
  TextField,
  Typography,
  Checkbox,
  FormControlLabel,
  Box,
  Grid,
} from '@mui/material';

function PingTemplateDashboard() {
  const { studyId } = useParams();
  const study = useStudy();

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
    '<PR_COMPLETED>',
  ];
  const messageOnlyVariables = ['<URL>'];
  const messageVariables = [...urlVariables, ...messageOnlyVariables];

  // State for listing
  const [pingTemplates, setPingTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [page, setPage] = useState(1);
  const [perPage] = useState(5);
  const [totalPages, setTotalPages] = useState(1);
  const [showCreateForm, setShowCreateForm] = useState(false);

  // React Hook Form
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
      studyLength: 7,
      scheduleMode: 'everyDay',
      everyDayPingsCount: 1,
      everyDayPings: [{ beginTime: '09:00', endTime: '17:00', nextDay: false }],
      perDaySchedule: [],
    },
  });

  const { handleSubmit, reset, watch } = methods;

  const studyLength = watch('studyLength');

  // Fetch existing Ping Templates
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

  // Delete a Ping Template
  const deletePingTemplate = async (templateId) => {
    if (!window.confirm('Are you sure you want to delete this ping template?')) return;

    try {
      await axios.delete(`/studies/${studyId}/ping_templates/${templateId}`);
      alert('Ping template deleted successfully.');
      fetchPingTemplates(studyId, page, perPage); // Refresh the list after deletion
    } catch (err) {
      console.error(err);
      alert('Error deleting ping template.');
    }
  };

  // Build schedule JSON for submission
  const buildScheduleJSON = (data) => {
    if (data.scheduleMode === 'everyDay') {
      const totalDays = parseInt(data.studyLength, 10) + 1;
      const scheduleArray = [];
      const startingDayNum = 1;
      for (let day = startingDayNum; day < totalDays; day++) {
        data.everyDayPings.forEach((ping) => {
          scheduleArray.push({
            begin_day_num: day,
            begin_time: ping.beginTime,
            end_day_num: ping.nextDay ? day + 1 : day,
            end_time: ping.endTime,
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
            end_time: ping.endTime,
          });
        });
      });
      return result;
    }
  };

  // Build reminder/expire strings
  const buildLatencyString = (hours, minutes) => {
    const h = parseInt(hours, 10);
    const m = parseInt(minutes, 10);
    if (h === 0 && m === 0) return null;
    let parts = [];
    if (h > 0) parts.push(`${h} hour${h > 1 ? 's' : ''}`);
    if (m > 0) parts.push(`${m} minute${m > 1 ? 's' : ''}`);
    return parts.join(' ');
  };

  // On Submit
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
        schedule: scheduleJSON,
      });

      reset();
      setShowCreateForm(false);
      fetchPingTemplates(studyId, page, perPage);
    } catch (err) {
      console.error(err);
      setError('Error creating ping template');
    }
  };

  // Pagination
  const handlePreviousPage = () => {
    if (page > 1) setPage((prev) => prev - 1);
  };
  const handleNextPage = () => {
    if (page < totalPages) setPage((prev) => prev + 1);
  };

  if (!studyId) {
    return <div>Error: Missing studyId in the URL.</div>;
  }

  // Function to format the schedule for display
  const formatSchedule = (schedule) => {
    if (!schedule || schedule.length === 0) {
      return 'No schedule';
    }

    // Check if the schedule is the same every day
    const uniqueDays = [...new Set(schedule.map((entry) => entry.begin_day_num))];
    const uniqueTimes = [
      ...new Set(
        schedule.map(
          (entry) =>
            `${entry.begin_time} - ${entry.end_time}${
              entry.end_day_num !== entry.begin_day_num ? ' (Next Day)' : ''
            }`
        )
      ),
    ];

    if (uniqueDays.length === parseInt(studyLength, 10) && uniqueTimes.length === 1) {
      // Schedule applies to every day with the same time
      return `Every day: ${uniqueTimes[0]}`;
    } else {
      // List individual days (limit to first 3 for brevity)
      return (
        schedule
          .slice(0, 3)
          .map((entry) => {
            const dayString = `Day ${entry.begin_day_num}: ${entry.begin_time} - ${entry.end_time}`;
            return entry.end_day_num !== entry.begin_day_num
              ? `${dayString} (ends Day ${entry.end_day_num})`
              : dayString;
          })
          .join('; ') + (schedule.length > 3 ? ' ...' : '')
      );
    }
  };

  // Function to format detailed schedule for tooltip
  const formatDetailedSchedule = (schedule) => {
    if (!schedule || schedule.length === 0) {
      return 'No schedule';
    }

    return schedule
      .map((entry) => {
        const { begin_day_num, begin_time, end_day_num, end_time } = entry;
        let detail = `Day ${begin_day_num}`;
        if (begin_day_num !== end_day_num) {
          detail += ` to Day ${end_day_num}`;
        }
        detail += `: ${begin_time} - ${end_time}`;
        return detail;
      })
      .join('\n');
  };

  return (
    <div style={{ margin: '2rem' }}>
      <Typography variant="h4" gutterBottom>
        Study: {study?.internal_name || 'Loading...'}
      </Typography>
      <StudyNav />

      <Button
        variant="contained"
        color={showCreateForm ? 'secondary' : 'primary'}
        onClick={() => setShowCreateForm(!showCreateForm)}
        sx={{ marginBottom: '1rem' }}
      >
        {showCreateForm ? 'Cancel' : 'Create New Ping Template'}
      </Button>

      {showCreateForm && (
        <Box component="section" sx={{ marginBottom: '2rem' }}>
          <Typography variant="h5" gutterBottom>
            Create a New Ping Template
          </Typography>

          <FormProvider {...methods}>
            <Box
              component="form"
              onSubmit={handleSubmit(onSubmit)}
              noValidate
              sx={{ maxWidth: 600 }}
            >
              <Grid container spacing={2}>
                {/* NAME */}
                <Grid item xs={12}>
                  <Controller
                    name="name"
                    control={methods.control}
                    rules={{ required: 'Name is required' }}
                    render={({ field, fieldState: { error } }) => (
                      <TextField
                        {...field}
                        label="Name"
                        fullWidth
                        required
                        error={!!error}
                        helperText={
                          error ? error.message : 'Enter the name of the ping template.'
                        }
                      />
                    )}
                  />
                </Grid>

                {/* URL with autocomplete */}
                <Grid item xs={12}>
                  <Controller
                    name="url"
                    control={methods.control}
                    render={({ field }) => (
                      <VariableAutoCompleteTextarea
                        {...field}
                        label="URL (optional)"
                        variableOptions={urlVariables}
                        onChange={(value) => field.onChange(value)}
                      />
                    )}
                  />
                </Grid>

                {/* URL TEXT */}
                {methods.watch('url') && (
                  <Grid item xs={12}>
                    <Controller
                      name="url_text"
                      control={methods.control}
                      rules={{ required: 'URL Text is required when URL is provided' }}
                      render={({ field, fieldState: { error } }) => (
                        <TextField
                          {...field}
                          label="URL Text"
                          fullWidth
                          required
                          error={!!error}
                          helperText={
                            error
                              ? error.message
                              : 'Enter the text that will be displayed for the URL.'
                          }
                        />
                      )}
                    />
                  </Grid>
                )}

                {/* MESSAGE with autocomplete */}
                <Grid item xs={12}>
                  <Controller
                    name="message"
                    control={methods.control}
                    rules={{ required: 'Message is required' }}
                    render={({ field, fieldState: { error } }) => (
                      <VariableAutoCompleteTextarea
                        {...field}
                        label="Message"
                        variableOptions={messageVariables}
                        error={!!error}
                        helperText={error ? error.message : ''}
                        onChange={(value) => field.onChange(value)}
                      />
                    )}
                  />
                </Grid>

                {/* REMINDER CHECKBOX */}
                <Grid item xs={12}>
                  <Controller
                    name="reminderEnabled"
                    control={methods.control}
                    render={({ field }) => (
                      <FormControlLabel
                        control={<Checkbox {...field} checked={field.value} />}
                        label="Enable Reminder"
                      />
                    )}
                  />
                </Grid>

                {methods.watch('reminderEnabled') && (
                  <>
                    <Grid item xs={6}>
                      <TextField
                        label="Reminder Hours"
                        type="number"
                        inputProps={{ min: 0 }}
                        fullWidth
                        {...methods.register('reminderHours')}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <TextField
                        label="Reminder Minutes"
                        type="number"
                        inputProps={{ min: 0, max: 59 }}
                        fullWidth
                        {...methods.register('reminderMinutes')}
                      />
                    </Grid>
                  </>
                )}

                {/* EXPIRE CHECKBOX */}
                <Grid item xs={12}>
                  <Controller
                    name="expireEnabled"
                    control={methods.control}
                    render={({ field }) => (
                      <FormControlLabel
                        control={<Checkbox {...field} checked={field.value} />}
                        label="Enable Expire"
                      />
                    )}
                  />
                </Grid>

                {methods.watch('expireEnabled') && (
                  <>
                    <Grid item xs={6}>
                      <TextField
                        label="Expire Hours"
                        type="number"
                        inputProps={{ min: 0 }}
                        fullWidth
                        {...methods.register('expireHours')}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <TextField
                        label="Expire Minutes"
                        type="number"
                        inputProps={{ min: 0, max: 59 }}
                        fullWidth
                        {...methods.register('expireMinutes')}
                      />
                    </Grid>
                  </>
                )}

                {/* STUDY LENGTH */}
                <Grid item xs={12}>
                  <TextField
                    label="Study Length (in days)"
                    type="number"
                    inputProps={{ min: 0 }}
                    fullWidth
                    {...methods.register('studyLength', { min: 0 })}
                  />
                </Grid>

                {/* SCHEDULE FORM */}
                <Grid item xs={12}>
                  <PingScheduleForm />
                </Grid>

                {/* SUBMIT BUTTON */}
                <Grid item xs={12}>
                  <Button type="submit" variant="contained" color="primary">
                    Create Ping Template
                  </Button>
                </Grid>
              </Grid>
            </Box>
          </FormProvider>
        </Box>
      )}

      {/* List existing Ping Templates */}
      <section>
        <DataTable
          data={pingTemplates.map((pt) => ({
            id: pt.id,
            name: pt.name,
            message: pt.message,
            url: pt.url,
            reminderLatency: pt.reminder_latency,
            expireLatency: pt.expire_latency,
            scheduleData: pt.schedule, // Keep raw schedule data
          }))}
          columns={[
            { label: 'ID', key: 'id' },
            { label: 'Name', key: 'name' },
            { label: 'Message', key: 'message' },
            { label: 'URL', key: 'url' },
            { label: 'Reminder Latency', key: 'reminderLatency' },
            { label: 'Expire Latency', key: 'expireLatency' },
            {
              label: 'Schedule',
              key: 'schedule',
              renderCell: (row) => (
                <Tooltip title={formatDetailedSchedule(row.scheduleData)}>
                  <span>{formatSchedule(row.scheduleData)}</span>
                </Tooltip>
              ),
            },
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