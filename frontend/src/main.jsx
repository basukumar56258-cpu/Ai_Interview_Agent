import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Brain, CheckCircle2, FileText, Play, RotateCcw, Upload } from 'lucide-react';
import './style.css';

const API = '/api';

async function request(url, options) {
	let response;
	try {
		response = await fetch(url, options);
	} catch {
		throw new Error('The backend is unavailable. Start FastAPI and try again.');
	}
	const data = await response.json().catch(() => ({}));
	if (!response.ok) {
		const detail = data.detail;
		throw new Error(typeof detail === 'string' ? detail : 'The request could not be completed.');
	}
	return data;
}

function App() {
	const [jobDescription, setJobDescription] = useState('');
	const [interviewType, setInterviewType] = useState('Mixed');
	const [difficulty, setDifficulty] = useState('Adaptive');
	const [questionCount, setQuestionCount] = useState(10);
	const [resumeText, setResumeText] = useState('');
	const [resumeName, setResumeName] = useState('');
	const [interviewId, setInterviewId] = useState('');
	const [question, setQuestion] = useState('');
	const [answer, setAnswer] = useState('');
	const [evaluation, setEvaluation] = useState(null);
	const [report, setReport] = useState(null);
	const [busy, setBusy] = useState(false);
	const [error, setError] = useState('');
	const [backendOnline, setBackendOnline] = useState(false);

	useEffect(() => {
		request('/health')
			.then(() => setBackendOnline(true))
			.catch(() => setBackendOnline(false));
	}, []);

	async function uploadResume(event) {
		const file = event.target.files?.[0];
		if (!file) return;
		setError('');
		setBusy(true);
		const form = new FormData();
		form.append('file', file);
		try {
			const data = await request(`${API}/resume/upload`, { method: 'POST', body: form });
			setResumeText(data.resume_text);
			setResumeName(data.filename);
		} catch (uploadError) {
			setError(uploadError.message);
			event.target.value = '';
		} finally {
			setBusy(false);
		}
	}

	async function startInterview(event) {
		event.preventDefault();
		if (!jobDescription.trim()) {
			setError('Please enter a job description before starting.');
			return;
		}
		setBusy(true);
		setError('');
		setEvaluation(null);
		setReport(null);
		try {
			const data = await request(`${API}/interview/create`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					job_description: jobDescription,
					interview_type: interviewType,
					difficulty,
					question_count: Number(questionCount),
					resume_text: resumeText,
				}),
			});
			setInterviewId(data.interview_id);
			setQuestion(data.first_question);
		} catch (startError) {
			setError(startError.message);
		} finally {
			setBusy(false);
		}
	}

	async function submitAnswer(event) {
		event.preventDefault();
		if (!answer.trim()) {
			setError('Please enter an answer before submitting.');
			return;
		}
		setBusy(true);
		setError('');
		try {
			const data = await request(`${API}/interview/${interviewId}/answer`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ answer }),
			});
			setEvaluation(data.evaluation);
			setQuestion(data.next_question || 'Interview complete');
			setAnswer('');
			setReport(data.report);
		} catch (answerError) {
			setError(answerError.message);
		} finally {
			setBusy(false);
		}
	}

	async function finishInterview() {
		setBusy(true);
		setError('');
		try {
			const data = await request(`${API}/interview/${interviewId}/finish`, { method: 'POST' });
			setReport(data.report);
			setQuestion('Interview complete');
		} catch (finishError) {
			setError(finishError.message);
		} finally {
			setBusy(false);
		}
	}

	function resetInterview() {
		setInterviewId('');
		setQuestion('');
		setAnswer('');
		setEvaluation(null);
		setReport(null);
		setError('');
	}

	return (
		<div className="app">
			<aside className="sidebar">
				<a className="brand" href="#dashboard">
					<span className="logo"><Brain size={22} /></span>
					<span><b>InterviewAI</b><small>Agentic Interview Coach</small></span>
				</a>
				<nav aria-label="Main navigation">
					<a className="active" href="#dashboard">Dashboard</a>
					<a href="#setup">New interview</a>
				</nav>
				<div className="sideCard">
					<b>Smart Interviewing</b>
					<p>Questions adapt to your profile, role, and answers.</p>
				</div>
			</aside>

			<main id="dashboard">
				<header>
					<div>
						<span className="eyebrow">AI-POWERED CAREER COACH</span>
						<h1>AI Interview Agent</h1>
						<p>Practice realistic interviews with an adaptive AI interviewer.</p>
					</div>
					<span className={backendOnline ? 'online' : 'offline'}>
						{backendOnline ? 'Backend online' : 'Backend offline'}
					</span>
				</header>

				<section className="hero">
					<span className="pill">MULTI-AGENT SYSTEM</span>
					<h2>Your personal AI interview coach.</h2>
					<p>Analyze your profile, plan the interview, evaluate answers, and get a final report.</p>
					<div className="flow">
						{['Profile', 'Plan', 'Interview', 'Evaluate', 'Follow-up', 'Report'].map((item, index) => (
							<div key={item}><span>{index + 1}</span>{item}</div>
						))}
					</div>
				</section>

				<section className="grid" id="setup">
					<form className="card" onSubmit={startInterview}>
						<div className="cardHead">
							<div><span className="eyebrow">SETUP</span><h3>Start a new interview</h3></div>
							<FileText aria-hidden="true" />
						</div>

						<label htmlFor="job-description">Job Description</label>
						<textarea
							id="job-description"
							value={jobDescription}
							onChange={(event) => setJobDescription(event.target.value)}
							placeholder="Paste the job description here..."
							required
							maxLength={20000}
						/>

						<label htmlFor="resume">Resume (optional)</label>
						<div className="uploadControl">
							<Upload size={17} aria-hidden="true" />
							<input id="resume" type="file" accept=".pdf,.docx,.txt" onChange={uploadResume} disabled={busy} />
						</div>
						{resumeName && <p className="fileName">{resumeName} ready</p>}

						<div className="fieldRow">
							<div>
								<label htmlFor="interview-type">Interview Type</label>
								<select id="interview-type" value={interviewType} onChange={(event) => setInterviewType(event.target.value)}>
									<option>Mixed</option><option>Technical</option><option>Behavioral</option>
								</select>
							</div>
							<div>
								<label htmlFor="difficulty">Difficulty</label>
								<select id="difficulty" value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
									<option>Adaptive</option><option>Easy</option><option>Medium</option><option>Hard</option>
								</select>
							</div>
							<div>
								<label htmlFor="question-count">Questions</label>
								<input id="question-count" type="number" min="1" max="20" value={questionCount} onChange={(event) => setQuestionCount(event.target.value)} />
							</div>
						</div>

						<button type="submit" disabled={busy || !jobDescription.trim()}>
							<Play size={17} aria-hidden="true" />
							{busy && !interviewId ? 'Analyzing...' : 'Analyze & Start Interview'}
						</button>
					</form>

					<section className="card" aria-labelledby="pipeline-title">
						<span className="eyebrow">AGENT PIPELINE</span>
						<h3 id="pipeline-title">Interview Progress</h3>
						{[
							['Profile Analyzer', 'Reviews resume and job requirements'],
							['Interview Planner', 'Builds a role-specific question plan'],
							['Interviewer', 'Asks context-aware questions'],
							['Answer Evaluator', 'Scores each candidate answer'],
							['Follow-up Agent', 'Clarifies answers when useful'],
							['Final Report', 'Summarizes strengths and improvements'],
						].map(([name, description], index) => (
							<div className="step" key={name}>
								<div className="stepIcon">{index + 1}</div>
								<div><b>{name}</b><small>{description}</small></div>
							</div>
						))}
					</section>
				</section>

				{error && <p className="notice error" role="alert">{error}</p>}

				{question && interviewId && (
					<section className="card interview" aria-live="polite">
						<div className="cardHead">
							<div><span className="eyebrow">LIVE INTERVIEW</span><h3>Question</h3></div>
							<button className="iconButton" type="button" onClick={resetInterview} title="Start a new interview" aria-label="Start a new interview">
								<RotateCcw size={18} />
							</button>
						</div>
						<div className="question">{question}</div>
						{!report && (
							<form onSubmit={submitAnswer}>
								<label htmlFor="answer">Your Answer</label>
								<textarea id="answer" value={answer} onChange={(event) => setAnswer(event.target.value)} placeholder="Type your answer..." maxLength={10000} />
								<div className="actionRow">
									<button type="submit" disabled={busy || !answer.trim()}><CheckCircle2 size={17} /> Submit Answer</button>
									<button className="secondaryButton" type="button" onClick={finishInterview} disabled={busy}>Finish Interview</button>
								</div>
							</form>
						)}
						{evaluation && (
							<div className="evaluation">
								<b>Latest evaluation{typeof evaluation.score === 'number' ? ` · ${evaluation.score}/100` : ''}</b>
								<p>{evaluation.feedback}</p>
								{evaluation.missing_points?.length > 0 && <p>Areas to cover: {evaluation.missing_points.join(', ')}</p>}
							</div>
						)}
						{report && (
							<div className="report">
								<h3>Final Report{typeof report.overall_score === 'number' ? ` · ${report.overall_score}/100` : ''}</h3>
								<div><b>Strengths</b><p>{report.strengths?.join(' · ') || 'None reported'}</p></div>
								<div><b>Improvements</b><p>{report.improvements?.join(' · ') || 'None reported'}</p></div>
								<div><b>Recommendations</b><p>{report.recommendations?.join(' · ') || 'None reported'}</p></div>
							</div>
						)}
					</section>
				)}
			</main>
		</div>
	);
}

const rootElement = document.getElementById('root');
const root = rootElement._reactRoot || createRoot(rootElement);
rootElement._reactRoot = root;
root.render(<App />);
