import React from 'react';
import { Link } from 'react-router-dom';

const EMAInstructions = () => {
  return (
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '1rem', paddingBottom: '3rem' }}>

      <h1>What Is EMA?</h1>
      <section style={{ marginBottom: '2rem' }}>
        <p>
          EMA stands for <strong>Ecological Momentary Assessment</strong> (also sometimes called experience sampling methodology or ESM). It is
          a research method that involves collecting real-time data from
          participants as they go about their everyday lives. By sending prompts
          (or “pings”) at various times during the day, EMA helps researchers
          capture <strong>in-the-moment</strong> experiences, behaviors, or
          feelings. This real-time approach reduces recall bias, provides richer
          data, and offers a more accurate picture of how participants think and
          act in their natural environments. A few common uses of EMA include:
        </p>
        <ul>
          <li>Monitoring mood or emotions</li>
          <li>Tracking health behaviors (e.g., diet, exercise)</li>
          <li>Understanding how particular environments interact with thoughts, feelings, or behaviors</li>
          <li>Delivering "just-in-time" interventions</li>
        </ul>
      </section>

      <h1>What is EMA Pingbot?</h1>
      <section style={{ marginBottom: '2rem' }}>
        <p>
          EMA Pingbot is a tool that helps researchers set up and manage EMA studies. 
          The application works in conjunction with the messaging app Telegram to deliver pings to participants that contain links to surveys in your chosen survey platform.
        </p>
        <p>
          Telegram is a widely used messaging platform offering secure communication across multiple devices. 
          By using Telegram, researchers can ensure that participants receive prompt and reliable notifications no matter what device they are using.
          Additionally, many people are already familiar with Telegram, making it easier and more comfortable for participants to engage with the study.
        </p>
        <p>
          One major advantage of EMA Pingbot is that it allows you to use the survey software of your choice--such as Qualtrics, REDCap, or any other platform to design and collect your data. 
          This flexibility means you can continue leveraging your existing survey designs and analytics tools while relying on EMA Pingbot to handle the scheduling and distribution of surveys to participants.
        </p>
      </section>


      <h1>How to set up a study with EMA Pingbot</h1>
      <section style={{ marginBottom: '2rem' }}>
        <p>
          This guide will walk you through the steps to set up an EMA study. 
          The process involves creating a study, creating ping templates which define the parameters of the individual pings, and onboarding participants. 
          By the end, you’ll have a fully functional EMA study ready to collect data. Let’s get started!
        </p>
        <h2>1. Create a Study Using the <Link to="/studies">Study Dashboard</Link></h2>
        <p>
          <strong>Public Name:</strong> Visible to participants. Choose something
          clear and recognizable (e.g., “Daily Mood Tracking Study”).
        </p>
        <p>
          <strong>Internal Name:</strong> Visible only to you and your team. You
          might include a study ID, version number, or other internal details
          (e.g., “MoodStudy2024_V1”).
        </p>

        <h3>Contact Message</h3>
        <p>
          In the Study Dashboard, you can set a <strong>contact message</strong>{' '}
          which participants can view if they have any questions or concerns.
          This message might include how to reach you or your support team. 
        </p>
        <blockquote style={{ fontStyle: 'italic', margin: '1rem 0' }}>
          “If you have any questions about the study, please email us at
          researchteam@example.com or call us at (555) 123-4567 between 9am–5pm
          EST.”
        </blockquote>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2>2. Create Ping Templates</h2>
        <p>
          After you've created a study, navigate to the study overview page by clicking the row containing your study from within the study dashboard. 
          Then click the "Ping Templates" tab and select "Create New Ping Template" to get started.
        </p>
        <p>
          A <strong>ping template</strong> defines the content and delivery
          settings for each type of EMA prompt. For example, you might have:
        </p>
        <ul>
          <li>
            Four daily EMA pings (prompting participants to report their current
            mood or behavior)
          </li>
          <li>One evening diary ping (to summarize the entire day)</li>
        </ul>

        <h3>Adding Variables in the Ping Template</h3>
        <p>
          When editing the ping template, you can include dynamic variables in
          your messages or links. Variables are wrapped in angle brackets and
          will be replaced with actual values when sent to participants. For
          instance:
        </p>
        <ul>
          <li>
            <strong>Variable:</strong> <code>&lt;DAY_NUM&gt;</code>
          </li>
          <li>
            <strong>Usage in Message:</strong> “This is your prompt for Day{' '}
            <code>&lt;DAY_NUM&gt;</code>.”
          </li>
          <li>
            <strong>Usage in URL:</strong>{' '}
            <code>https://example.com/survey?day=&lt;DAY_NUM&gt;</code>
          </li>
        </ul>
        <p>
          Typing <code>&lt;</code> in the ping template editor will display a
          list of possible variables you can insert. This helps you track
          participant progress and streamline data analysis when you download
          responses from external survey tools (e.g., Qualtrics).
        </p>

        <h3>Reminders and Expiration</h3>
        <p>
          Within each ping template, you can configure:
        </p>
        <ul>
          <li>
            <strong>Reminders:</strong> Set if and after how long a reminder
            should be sent if a participant has not responded.
          </li>
          <li>
            <strong>Expiration:</strong> Decide if and when the ping link
            becomes inactive, preventing responses after a certain time.
          </li>
        </ul>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h3>Scheduling Pings</h3>
        <p>
          Scheduling pings is done by defining blocks of time (e.g., 9am-12pm) within which a ping will be sent to the participant at a random time. There are two ways to set the schedule for each ping template:
        </p>
        <ol>
          <li>
            <strong>Every Day:</strong> Define one or more “ping time blocks”
            that will be repeated every day for the duration of the defined study length. 
            <br />
            <em>Note:</em> Using “Every Day” means pings will start arriving the
            day after a participant enrolls.
          </li>
          <li>
            <strong>Per Day:</strong> Provides more granular control allowing you to set ping blocks for each day of the study invididually. (e.g., to send a special
            exit survey on the final day). This option will also allow you to sends pings on the day of enrollment.
          </li>
        </ol>
        <p>
          <strong>Handling Time Blocks Crossing Midnight:</strong> If your ping
          window crosses midnight (e.g., 10:00 PM to 2:00 AM), enable the “Next
          Day” checkbox to indicate that the end time of the ping block refers to the following
          day.
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2>3. Get the Participant Enrollment Link</h2>
        <p>
          After creating and configuring your ping templates, go back to the{' '}
          <strong>Study Overview</strong> to retrieve the enrollment link.
          Participants will use this link to join your study.
        </p>

        <h3>Including a Unique Participant ID</h3>
        <p>
          You must include a unique ID for each participant in the link. 
          If you do not include a unique ID for each participant, you would not be able to match the survey entries to participants so it is required by the app.
          A common way to enroll participants is to embed the EMA enrollment link in a Qualtrics survey where you might collect some initial information from participants.
          If you take this approach, you can create a participant ID variable within Qualtrics and embed that variable in the EMA Pingbot enrollment link. 
          The Qualtrics variable might look something like this and this is what you would enter into field for Participant ID within the Pingbot application.
        </p>
        <pre
          style={{
            background: '#f4f4f4',
            padding: '0.5rem',
            overflow: 'auto',
          }}
        >
          
          <div dangerouslySetInnerHTML={{ __html: '<code>${e://Field/participant_id}</code>' }} />
        </pre>
        <p>
          When properly configured, Qualtrics will replace this placeholder with
          the actual participant ID in the URL. Refer to{' '}
          <a
            href="https://www.qualtrics.com/support/fr/survey-platform/survey-module/survey-flow/standard-elements/embedded-data/#SettingValuesFromTheSurveyURL"
            target="_blank"
            rel="noopener noreferrer"
          >
            Qualtrics documentation on embedded data
          </a>{' '}
          to learn more (and be sure to test thoroughly!)
        </p>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2>4. Participant Onboarding</h2>
        <ol>
          <li>
            <strong>Provide Link:</strong> Share the enrollment link with your
            participants via email, Qualtrics, etc.
          </li>
          <li>
            <strong>Time Zone Selection:</strong> Participants select their time
            zone when following the link.
          </li>
          <li>
            <strong>Unique Enrollment Code:</strong> After selecting a time
            zone, participants receive a unique code.
          </li>
          <li>
            <strong>Telegram Enrollment:</strong> Participants use that code to
            enroll in your study on Telegram.
          </li>
        </ol>
      </section>

      <section style={{ marginBottom: '2rem' }}>
        <h2>Final Notes</h2>
        <ul>
          <li>
            <strong>Testing:</strong> Test the entire flow yourself or with a
            small pilot group before launching. I cannot stress enough how important this is.
            Be sure to look thoroughly at the data you receive to ensure it is what you expect.
          </li>
          <li>
            <strong>Monitoring:</strong> Regularly check the Study Dashboard for
            participant progress. Keep an eye out for participants who are not completing pings, by looking at the ping dashboard.
            Also be sure to check the participant dashboard to see if any participants have not successfully linked their Telegram account.
          </li>
          <li>
            <strong>Support:</strong> Keep your contact message up to date so
            participants know how to reach you if they have questions.
          </li>
        </ul>
      </section>

      <p>
        We hope this guide helps you set up and manage your EMA study
        efficiently. Good luck with your research!
      </p>
    </div>

  );
};

export default EMAInstructions;