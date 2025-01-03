import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Link as MUILink,
  List,
  ListItem,
  ListItemText,
  Divider,
  Paper,
} from '@mui/material';

const EMAInstructions = () => {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Title: What Is EMA? */}
      <Typography variant="h4" gutterBottom>
        What Is EMA?
      </Typography>
      <Box mb={4}>
        <Typography paragraph>
          EMA stands for <strong>Ecological Momentary Assessment</strong> (also
          sometimes called experience sampling methodology or ESM). It is a
          research method that involves collecting real-time data from
          participants as they go about their everyday lives. By sending prompts
          (or “pings”) at various times during the day, EMA helps researchers
          capture <strong>in-the-moment</strong> experiences, behaviors, or
          feelings. This real-time approach reduces recall bias, provides richer
          data, and offers a more accurate picture of how participants think and
          act in their natural environments. A few common uses of EMA include:
        </Typography>

        {/* Example list using MUI List */}
        <List sx={{ listStyleType: 'disc', pl: 4 }}>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText primary="Monitoring mood or emotions" />
          </ListItem>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText primary="Tracking health behaviors (e.g., diet, exercise)" />
          </ListItem>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText primary="Understanding how particular environments interact with thoughts, feelings, or behaviors" />
          </ListItem>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText primary='Delivering "just-in-time" interventions' />
          </ListItem>
        </List>
      </Box>

      <Divider sx={{ mb: 4 }} />

      {/* Title: What is EMA Pingbot? */}
      <Typography variant="h4" gutterBottom>
        What is EMA Pingbot?
      </Typography>
      <Box mb={4}>
        <Typography paragraph>
          EMA Pingbot is a tool that helps researchers set up and manage EMA
          studies. The application works in conjunction with the messaging app
          Telegram to deliver pings to participants that contain links to
          surveys in your chosen survey platform.
        </Typography>
        <Typography paragraph>
          Telegram is a widely used messaging platform offering secure
          communication across multiple devices. By using Telegram, researchers
          can ensure that participants receive prompt and reliable notifications
          no matter what device they are using. Additionally, many people are
          already familiar with Telegram, making it easier and more comfortable
          for participants to engage with the study.
        </Typography>
        <Typography paragraph>
          One major advantage of EMA Pingbot is that it allows you to use the
          survey software of your choice—such as Qualtrics, REDCap, or any other
          platform to design surveys and collect your data. This flexibility means you
          can continue leveraging your existing survey design and analytics
          tools while relying on EMA Pingbot to handle the scheduling and
          distribution of surveys to participants.
        </Typography>
      </Box>

      <Divider sx={{ mb: 4 }} />

      {/* Title: How to set up a study */}
      <Typography variant="h4" gutterBottom>
        How to set up a study with EMA Pingbot
      </Typography>
      <Box mb={4}>
        <Typography paragraph>
          This guide will walk you through the steps to set up an EMA study. The
          process involves creating a study, creating ping templates which
          define the parameters of the individual pings, and onboarding
          participants. By the end, you’ll have a fully functional EMA study
          ready to collect data. Let’s get started!
        </Typography>

        {/* Step 1 */}
        <Typography variant="h5" gutterBottom>
          1. Create a Study Using the{' '}
          <RouterLink to="/studies">Study Dashboard</RouterLink>
        </Typography>
        <Typography paragraph>
          <strong>Public Name:</strong> Visible to participants. Choose something
          clear and recognizable (e.g., “Daily Mood Tracking Study”).
        </Typography>
        <Typography paragraph>
          <strong>Internal Name:</strong> Visible only to you and your team. You
          might include a study ID, version number, or other internal details
          (e.g., “MoodStudy2024_V1”).
        </Typography>

        <Typography variant="subtitle1" gutterBottom>
          Contact Message
        </Typography>
        <Typography paragraph>
          In the Study Dashboard, you can set a <strong>contact message</strong>{' '}
          which participants can access in Telegram if they have any questions
          or concerns. This message might include how to reach you or your
          support team.
        </Typography>

        {/* Blockquote style with Paper */}
        <Paper
          variant="outlined"
          sx={{
            p: 2,
            fontStyle: 'italic',
            backgroundColor: (theme) => theme.palette.action.hover,
            mb: 2,
          }}
        >
          “If you have any questions about the study, please email us at
          researchteam@example.com or call us at (555) 123-4567 between 9am–5pm
          EST.”
        </Paper>

        <Typography paragraph>
        Please note that certain platforms (e.g. Prolific) have privacy policies that prevent researchers from collecting contact information from participants. 
        In these cases, your contact message should direct participants to contact you through the platform’s messaging system 
        in order to prevent exposing the participants' own contact information to you.
        </Typography>
      </Box>

      {/* Step 2 */}
      <Box mb={4}>
        <Typography variant="h5" gutterBottom>
          2. Create Ping Templates
        </Typography>
        <Typography paragraph>
          After you've created a study, navigate to the study overview page by
          clicking the row containing your study from within the study
          dashboard. Then click the &quot;Ping Templates&quot; tab and select
          &quot;Create New Ping Template&quot; to get started.
        </Typography>
        <Typography paragraph>
          A <strong>ping template</strong> defines the content and delivery
          settings for each type of EMA prompt. For example, you might have:
        </Typography>

        <List sx={{ listStyleType: 'disc', pl: 4 }}>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText
              primary="A ping template defining four daily EMA pings (prompting participants to report their
              current mood or behavior)"
            />
          </ListItem>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText primary="A ping template defining one evening diary ping (to summarize the entire day)" />
          </ListItem>
        </List>

        <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
          Adding Variables in the Ping Template
        </Typography>
        <Typography paragraph>
          When editing the ping template, you can include dynamic variables in
          your messages or links. Variables are wrapped in angle brackets and
          will be replaced with actual values when sent to participants. For
          instance:
        </Typography>
        <List sx={{ pl: 4 }}>
          <ListItem>
            <ListItemText
              primary={
                <>
                  <strong>Variable:</strong> <code>&lt;DAY_NUM&gt;</code>
                </>
              }
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary={
                <>
                  <strong>Usage in Message:</strong> “This is your prompt for
                  Day <code>&lt;DAY_NUM&gt;</code>.”
                </>
              }
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary={
                <>
                  <strong>Usage in URL:</strong>{' '}
                  <code>https://example.com/survey?day=&lt;DAY_NUM&gt;</code>
                </>
              }
            />
          </ListItem>
        </List>
        <Typography paragraph>
          Typing <code>&lt;</code> in the ping template editor will display a
          list of possible variables you can insert. This helps you track
          participant progress and streamline data analysis when you download
          responses from external survey tools (e.g., Qualtrics).
        </Typography>

        <Typography variant="subtitle1" gutterBottom>
          Reminders and Expiration
        </Typography>
        <Typography paragraph>
          Within each ping template, you can configure:
        </Typography>
        <List sx={{ listStyleType: 'disc', pl: 4 }}>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText
              primary={
                <>
                  <strong>Reminders:</strong> Set if and after how long a
                  reminder should be sent if a participant has not responded.
                </>
              }
            />
          </ListItem>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText
              primary={
                <>
                  <strong>Expiration:</strong> Decide if and when the ping link
                  becomes inactive, preventing responses after a certain time.
                </>
              }
            />
          </ListItem>
        </List>
      </Box>

      {/* Scheduling Pings */}
      <Box mb={4}>
        <Typography variant="subtitle1" gutterBottom>
          Scheduling Pings
        </Typography>
        <Typography paragraph>
          Scheduling pings is done by defining blocks of time (e.g., 9am–12pm)
          within which a ping will be sent to the participant at a random time.
          There are two ways to set the schedule for each ping template:
        </Typography>
        <List sx={{ listStyleType: 'decimal', pl: 4 }}>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText
              primary={
                <>
                  <strong>Every Day:</strong> Define one or more “ping time
                  blocks” that will be repeated every day for the duration of
                  the defined study length. <br />
                  <em>
                    Note: Using “Every Day” means pings will start arriving the
                    day after a participant enrolls.
                  </em>
                </>
              }
            />
          </ListItem>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText
              primary={
                <>
                  <strong>Per Day:</strong> Provides more granular control
                  allowing you to set ping blocks for each day of the study
                  individually. (e.g., to send a special exit survey on the
                  final day). This option will also allow you to send pings on
                  the day of enrollment.
                </>
              }
            />
          </ListItem>
        </List>
        <Typography paragraph>
          <strong>Handling Time Blocks Crossing Midnight:</strong> If your ping
          window crosses midnight (e.g., 10:00 PM to 2:00 AM), enable the “Next
          Day” checkbox to indicate that the end time of the ping block refers
          to the following day.
        </Typography>
      </Box>

      {/* Step 3 */}
      <Box mb={4}>
        <Typography variant="h5" gutterBottom>
          3. Get the Participant Enrollment Link
        </Typography>
        <Typography paragraph>
          After creating and configuring your ping templates, go back to the{' '}
          <strong>Study Overview</strong> to retrieve the enrollment link.
          Participants will use this link to join your study.
        </Typography>

        <Typography variant="subtitle1" gutterBottom>
          Including a Unique Participant ID
        </Typography>
        <Typography paragraph>
          In the enrollment link you provide to participants, you must include a unique ID for each participant. If you
          do not include a unique ID for each participant, you would not be able
          to match the survey entries to participants, so it is required by the
          app. A common way to enroll participants is to embed the EMA enrollment
          link in a Qualtrics survey where you might collect some initial
          information from participants. If you take this approach, you can
          create a participant ID variable within Qualtrics and embed that
          variable in the EMA Pingbot enrollment link that you place within your entry survey. The Qualtrics variable
          might look something like what is written below, and so that is what you would enter into
          the field for Participant ID within the Pingbot application.
        </Typography>

        {/* Code block */}
        <Box
          component="pre"
          sx={{
            backgroundColor: (theme) => theme.palette.grey[100],
            p: 2,
            overflowX: 'auto',
            mb: 2,
            borderRadius: 1,
          }}
        >
          <code>${'{e://Field/participant_id}'}</code>
        </Box>

        <Typography paragraph>
          When properly configured, Qualtrics will replace this placeholder with
          the actual participant ID in the URL. Refer to{' '}
          <MUILink
            href="https://www.qualtrics.com/support/fr/survey-platform/survey-module/survey-flow/standard-elements/embedded-data/#SettingValuesFromTheSurveyURL"
            target="_blank"
            rel="noopener noreferrer"
          >
            Qualtrics documentation on embedded data
          </MUILink>{' '}
          to learn more (and be sure to test thoroughly!).
        </Typography>
      </Box>

      {/* Step 4 */}
      <Box mb={4}>
        <Typography variant="h5" gutterBottom>
          4. Participant Onboarding
        </Typography>
        <List sx={{ listStyleType: 'decimal', pl: 4 }}>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText
              primary="Provide Link: Share the enrollment link found in the study overview page with your participants via email, Qualtrics, etc."
            />
          </ListItem>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText
              primary="Time Zone Selection: Participants follow the link and are prompted to select their time zone."
            />
          </ListItem>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText
              primary="Unique Enrollment Code: After selecting a time zone, participants receive a unique code and are instructed on how to download Telegram and submit their code to the bot on Telegram."
            />
          </ListItem>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText
              primary="Telegram Enrollment: Participants submit their unique code to the bot on Telegram at which point they are enrolled in the study and will receive the pings designated by your ping templates."
            />
          </ListItem>
        </List>
      </Box>

      {/* Final Notes */}
      <Box mb={4}>
        <Typography variant="h5" gutterBottom>
          Final Notes
        </Typography>
        <List sx={{ listStyleType: 'disc', pl: 4 }}>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText
              primary={
                <>
                  <strong>Testing:</strong> Test the entire flow yourself or
                  with a small pilot group before launching. I cannot stress
                  enough how important this is. Be sure to look thoroughly at
                  the data you receive to ensure it is what you expect.
                </>
              }
            />
          </ListItem>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText
              primary={
                <>
                  <strong>Monitoring:</strong> Regularly check the Study
                  Dashboard for participant progress. Keep an eye out for
                  participants who are not completing pings by looking at the
                  ping dashboard. Also be sure to check the participant
                  dashboard to see if any participants have not successfully
                  linked their Telegram account.
                </>
              }
            />
          </ListItem>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText
              primary={
                <>
                  <strong>Participant Support:</strong> Keep your contact message up to date
                  so participants know how to reach you if they have questions.
                </>
              }
            />
          </ListItem>
          <ListItem sx={{ display: 'list-item' }}>
            <ListItemText
              primary={
                <>
                  <strong>Researcher Support and Feedback:</strong> If you run into any issues, you can open a feedback form by clicking in the bottom left corner of the screen. If anything seems off or you run into any bugs, I really appreciate if you would take a second or two to report it via the feedback form. Thank you!
                </>
              }
            />
          </ListItem>
        </List>
      </Box>

      <Typography paragraph>
        I hope this guide helps you set up and manage your EMA study efficiently.
        Good luck with your research!
      </Typography>
    </Container>
  );
};

export default EMAInstructions;