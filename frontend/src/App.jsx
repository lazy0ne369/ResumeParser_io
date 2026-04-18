import { useEffect, useState, startTransition } from 'react'
import axios from 'axios'
import { AnimatePresence, motion } from 'framer-motion'
import {
  ArrowLeft,
  BrainCircuit,
  BriefcaseBusiness,
  Download,
  FileUp,
  GraduationCap,
  Mail,
  MapPin,
  Moon,
  Phone,
  Sparkles,
  Sun,
} from 'lucide-react'
import './App.css'

const SESSION_STORAGE_KEY = 'resume-parser-session'
const THEME_STORAGE_KEY = 'resume-parser-theme'

const sampleResume = `Aarav Sharma
NLP Engineer
aarav.sharma@email.com | +91 98765 43210 | Bengaluru, India
https://www.linkedin.com/in/aarav-sharma | https://github.com/aaravsharma

PROFESSIONAL SUMMARY
NLP-focused software engineer with experience building resume screening workflows, chat assistants, and information extraction systems using Python, FastAPI, React, and transformer-based tooling.

TECHNICAL SKILLS
Python, FastAPI, React, JavaScript, SQL, NLP, Machine Learning, spaCy, NLTK, Docker, GitHub Actions, PostgreSQL

WORK EXPERIENCE
NLP Engineer
TalentStack AI
Jan 2023 - Present
Built a resume parser pipeline to extract contact details, skills, projects, and education from unstructured PDF resumes.
Created matching rules for recruiters to shortlist candidates faster.

Software Developer Intern
PeopleOps Labs
Jun 2022 - Dec 2022
Developed internal tools with React and Flask for hiring teams.

EDUCATION
Bachelor of Technology in Computer Science
Visvesvaraya Technological University

PROJECTS
Resume Parser Dashboard
Job matching engine using NLP embeddings and recruiter-ready scorecards.`

function readStoredSession() {
  if (typeof window === 'undefined') {
    return null
  }

  const stored = window.sessionStorage.getItem(SESSION_STORAGE_KEY)
  if (!stored) {
    return null
  }

  try {
    return JSON.parse(stored)
  } catch {
    window.sessionStorage.removeItem(SESSION_STORAGE_KEY)
    return null
  }
}

function readStoredTheme() {
  if (typeof window === 'undefined') {
    return 'light'
  }

  const stored = window.localStorage.getItem(THEME_STORAGE_KEY)
  if (stored === 'dark' || stored === 'light') {
    return stored
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const emptyResult = {
  profile: {},
  highlights: {},
  skillBuckets: {},
  sections: {},
  structuredSections: [],
  experienceTimeline: [],
  learningSignals: [],
  insights: [],
}

const panelTransition = {
  type: 'spring',
  stiffness: 180,
  damping: 22,
}

const staggerContainer = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.07,
      delayChildren: 0.04,
    },
  },
}

const riseIn = {
  hidden: { opacity: 0, y: 18, filter: 'blur(6px)' },
  show: {
    opacity: 1,
    y: 0,
    filter: 'blur(0px)',
    transition: {
      duration: 0.42,
      ease: [0.22, 1, 0.36, 1],
    },
  },
}

const softIn = {
  hidden: { opacity: 0, scale: 0.985 },
  show: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.38,
      ease: [0.22, 1, 0.36, 1],
    },
  },
}

function titleCase(value) {
  return value.replace(/_/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function renderStructuredSection(section) {
  if (section.type === 'summary') {
    return (
      <motion.article className="structured-section" key={section.key} variants={riseIn}>
        <div className="section-label">{section.title}</div>
        <div className="entry-stack">
          {(section.paragraphs || []).map((paragraph) => (
            <motion.div className="entry-card" key={paragraph} variants={softIn}>
              <p>{paragraph}</p>
            </motion.div>
          ))}
        </div>
      </motion.article>
    )
  }

  if (section.type === 'education' || section.type === 'projects' || section.type === 'experience') {
    return (
      <motion.article className="structured-section" key={section.key} variants={riseIn}>
        <div className="section-label">{section.title}</div>
        <div className="entry-stack">
          {(section.entries || []).map((entry, index) => (
            <motion.div className="entry-card" key={`${section.key}-${index}`} variants={softIn}>
              <div className="entry-header">
                <strong>{entry.name || entry.title}</strong>
                {entry.dateRange ? <small>{entry.dateRange}</small> : null}
              </div>
              {entry.subtitle ? <p className="entry-subtitle">{entry.subtitle}</p> : null}
              {entry.institution ? <p className="entry-subtitle">{entry.institution}</p> : null}
              {entry.cgpa || entry.expected ? (
                <div className="meta-row">
                  {entry.cgpa ? <span>CGPA: {entry.cgpa}</span> : null}
                  {entry.expected ? <span>Expected: {entry.expected}</span> : null}
                </div>
              ) : null}
              {entry.stack?.length ? (
                <div className="chip-wrap compact">
                  {entry.stack.map((item) => (
                    <span className="chip muted" key={item}>
                      {item}
                    </span>
                  ))}
                </div>
              ) : null}
              {entry.details?.length ? (
                <ul className="bullet-list">
                  {entry.details.map((detail) => (
                    <li key={detail}>{detail}</li>
                  ))}
                </ul>
              ) : null}
            </motion.div>
          ))}
        </div>
      </motion.article>
    )
  }

  if (section.type === 'skills' || section.type === 'categorized') {
    return (
      <motion.article className="structured-section" key={section.key} variants={riseIn}>
        <div className="section-label">{section.title}</div>
        <div className="group-stack">
          {(section.groups || []).map((group) => (
            <motion.div className="entry-card" key={`${section.key}-${group.label}`} variants={softIn}>
              <div className="entry-header">
                <strong>{group.label}</strong>
              </div>
              <div className="chip-wrap compact">
                {(group.items || []).map((item) => (
                  <span className={`chip ${item.status ? 'status' : ''}`} key={`${group.label}-${item.name}`}>
                    {item.name}
                    {item.status ? ` (${item.status})` : ''}
                  </span>
                ))}
              </div>
              {group.notes?.length ? (
                <ul className="bullet-list">
                  {group.notes.map((note) => (
                    <li key={note}>{note}</li>
                  ))}
                </ul>
              ) : null}
            </motion.div>
          ))}
        </div>
      </motion.article>
    )
  }

  return null
}

function App() {
  const storedSession = readStoredSession()
  const [resumeText, setResumeText] = useState(storedSession?.resumeText || '')
  const [selectedFile, setSelectedFile] = useState(null)
  const [selectedFileName, setSelectedFileName] = useState(storedSession?.selectedFileName || '')
  const [theme, setTheme] = useState(readStoredTheme)
  const [isParsing, setIsParsing] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [result, setResult] = useState(storedSession?.result || emptyResult)
  const [activeView, setActiveView] = useState(storedSession?.activeView || 'input')

  const topSkills = result.highlights?.topSkills || []
  const skillBuckets = Object.entries(result.skillBuckets || {}).filter(([, items]) => items?.length)
  const structuredSections = result.structuredSections || []
  const learningSignals = result.learningSignals || []
  const hasParsedOutput = Boolean(
    structuredSections.length ||
      result.experienceTimeline?.length ||
      result.insights?.length ||
      topSkills.length ||
      Object.keys(result.profile || {}).length,
  )

  useEffect(() => {
    window.sessionStorage.setItem(
      SESSION_STORAGE_KEY,
      JSON.stringify({
        resumeText,
        selectedFileName,
        result,
        activeView,
      }),
    )
  }, [resumeText, selectedFileName, result, activeView])

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    window.localStorage.setItem(THEME_STORAGE_KEY, theme)
  }, [theme])

  async function handleParse(event) {
    event.preventDefault()

    const formData = new FormData()
    if (resumeText.trim()) {
      formData.append('resume_text', resumeText.trim())
    }
    if (selectedFile) {
      formData.append('resume_file', selectedFile)
    }

    if (![...formData.keys()].length) {
      setErrorMessage('Add resume text or choose a file before parsing.')
      return
    }

    try {
      setIsParsing(true)
      setErrorMessage('')
      const response = await axios.post('/api/parse', formData)
      startTransition(() => {
        setResult(response.data)
        setActiveView('output')
      })
    } catch (error) {
      setErrorMessage(
        error.response?.data?.detail || 'Unable to parse the resume right now. Check that the backend is running.',
      )
    } finally {
      setIsParsing(false)
    }
  }

  function handleFileChange(event) {
    const file = event.target.files?.[0] || null
    setSelectedFile(file)
    setSelectedFileName(file?.name || '')
    setResult(emptyResult)
    setActiveView('input')
    setErrorMessage('')
  }

  function handleResetSample() {
    setResumeText('')
    setSelectedFile(null)
    setSelectedFileName('')
    setErrorMessage('')
    setResult(emptyResult)
    setActiveView('input')
  }

  function handleLoadSample() {
    setResumeText(sampleResume)
    setSelectedFile(null)
    setSelectedFileName('')
    setErrorMessage('')
    setActiveView('input')
  }

  function handleDownloadOutput() {
    if (!hasParsedOutput) {
      return
    }

    const payload = {
      generatedAt: new Date().toISOString(),
      sourceFile: selectedFile?.name || selectedFileName || null,
      parsed: result,
    }

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
    const objectUrl = window.URL.createObjectURL(blob)
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const anchor = document.createElement('a')
    anchor.href = objectUrl
    anchor.download = `resume-parse-output-${timestamp}.json`
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    window.URL.revokeObjectURL(objectUrl)
  }

  return (
    <div className="app-shell">
      <motion.header className="app-header" initial="hidden" animate="show" variants={staggerContainer}>
        <motion.div
          className="header-glow header-glow-left"
          animate={{ y: [0, -8, 0] }}
          transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="header-glow header-glow-right"
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut', delay: 0.4 }}
        />
        <motion.div variants={riseIn}>
          <div className="header-top">
            <div className="eyebrow">
              <Sparkles size={15} />
              Resume Parser
            </div>
            <button
              type="button"
              className="theme-toggle"
              onClick={() => setTheme((current) => (current === 'dark' ? 'light' : 'dark'))}
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
              {theme === 'dark' ? 'Light mode' : 'Dark mode'}
            </button>
          </div>
          <h1>Structured resume parsing</h1>
          <p className="hero-text">
            Input once, parse, then review the extracted candidate structure in a dedicated result view.
          </p>
        </motion.div>
      </motion.header>

      <section className="stage-shell">
        <AnimatePresence mode="wait">
          {activeView === 'input' ? (
            <motion.form
              key="input-view"
              className="stage-panel"
              onSubmit={handleParse}
              layout
              initial={{ opacity: 0, y: 24, scale: 0.985 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -18, scale: 0.985 }}
              transition={panelTransition}
            >
              <motion.div className="stage-head" variants={staggerContainer} initial="hidden" animate="show">
                <motion.div variants={riseIn}>
                  <span className="panel-kicker">Input</span>
                  <h2>Resume input</h2>
                  <p className="panel-copy">
                    Upload a resume or paste raw content. Parsing opens the extracted view in the same workspace.
                  </p>
                </motion.div>
                <motion.div
                  className="panel-icon"
                  variants={softIn}
                  whileHover={{ rotate: -8, scale: 1.05 }}
                  transition={{ duration: 0.22 }}
                >
                  <FileUp size={20} />
                </motion.div>
              </motion.div>

              <div className="input-layout">
                <motion.div className="input-main" variants={staggerContainer} initial="hidden" animate="show">
                  <motion.label className="upload-zone" variants={riseIn}>
                    <input type="file" accept=".pdf,.doc,.docx,.txt" onChange={handleFileChange} />
                    <span>{selectedFile?.name || selectedFileName || 'Choose a resume file'}</span>
                    <small>Supported: PDF, DOCX, TXT</small>
                  </motion.label>

                  <motion.textarea
                    variants={riseIn}
                    value={resumeText}
                    onChange={(event) => setResumeText(event.target.value)}
                    placeholder="Paste raw resume text here..."
                    rows={20}
                  />

                  <motion.div className="action-row" variants={riseIn}>
                    <motion.button
                      type="submit"
                      className="primary-button"
                      disabled={isParsing}
                      whileHover={{ y: -2, scale: 1.01 }}
                      whileTap={{ scale: 0.985 }}
                    >
                      <BrainCircuit size={18} />
                      {isParsing ? 'Parsing resume...' : 'Parse resume'}
                    </motion.button>
                    <motion.button
                      type="button"
                      className="ghost-button"
                      onClick={handleResetSample}
                      whileHover={{ y: -2 }}
                      whileTap={{ scale: 0.985 }}
                    >
                      Clear workspace
                    </motion.button>
                  </motion.div>

                  <AnimatePresence>
                    {errorMessage ? (
                      <motion.p
                        className="error-banner"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                      >
                        {errorMessage}
                      </motion.p>
                    ) : null}
                  </AnimatePresence>
                </motion.div>

                <motion.aside className="input-aside" variants={staggerContainer} initial="hidden" animate="show">
                  <motion.div className="aside-card" variants={riseIn}>
                    <span className="section-label">What gets extracted</span>
                    <ul className="bullet-list">
                      <li>Top-level sections like education, projects, experience, achievements, and additional info.</li>
                      <li>Subheadings such as skill groups, workshop blocks, and competitive programming sections.</li>
                      <li>Learning markers like `(learning)` and `(practicing)` as explicit structured signals.</li>
                    </ul>
                  </motion.div>

                  <motion.div className="aside-card" variants={riseIn}>
                    <span className="section-label">Best results</span>
                    <ul className="bullet-list">
                      <li>Upload the original PDF when possible.</li>
                      <li>Keep headings and labels intact.</li>
                      <li>Use the output view to verify grouping and nested entries.</li>
                    </ul>
                    <motion.button
                      type="button"
                      className="ghost-button aside-button"
                      onClick={handleLoadSample}
                      whileHover={{ y: -2 }}
                      whileTap={{ scale: 0.985 }}
                    >
                      Load sample resume
                    </motion.button>
                  </motion.div>
                </motion.aside>
              </div>
            </motion.form>
          ) : (
            <motion.section
              key="output-view"
              className="stage-panel"
              layout
              initial={{ opacity: 0, y: 24, scale: 0.985 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -18, scale: 0.985 }}
              transition={panelTransition}
            >
              <motion.div className="stage-head output-head" variants={staggerContainer} initial="hidden" animate="show">
                <motion.div className="head-actions" variants={riseIn}>
                  <div className="output-toolbar">
                    <motion.button
                      type="button"
                      className="back-button"
                      onClick={() => setActiveView('input')}
                      whileHover={{ x: -2 }}
                      whileTap={{ scale: 0.985 }}
                    >
                      <ArrowLeft size={16} />
                      Back to input
                    </motion.button>
                    <motion.button
                      type="button"
                      className="ghost-button download-button"
                      onClick={handleDownloadOutput}
                      disabled={!hasParsedOutput}
                      whileHover={{ y: -2 }}
                      whileTap={{ scale: 0.985 }}
                    >
                      <Download size={16} />
                      Download output
                    </motion.button>
                  </div>
                  <div>
                    <span className="panel-kicker">Output</span>
                    <h2>Parsed summary</h2>
                    <p className="panel-copy">
                      Structured extraction from the uploaded or pasted resume.
                    </p>
                  </div>
                </motion.div>

                <motion.div className="metric-row" variants={staggerContainer}>
                  <motion.article variants={softIn} whileHover={{ y: -2 }}>
                    <strong>{topSkills.length || 0}</strong>
                    <span>Skills</span>
                  </motion.article>
                  <motion.article variants={softIn} whileHover={{ y: -2 }}>
                    <strong>{result.experienceTimeline?.length || 0}</strong>
                    <span>Timeline</span>
                  </motion.article>
                  <motion.article variants={softIn} whileHover={{ y: -2 }}>
                    <strong>{result.highlights?.learningSignals ?? 0}</strong>
                    <span>Learning</span>
                  </motion.article>
                </motion.div>
              </motion.div>

              <motion.div className="profile-card profile-card-wide" variants={riseIn} initial="hidden" animate="show">
                <div>
                  <p className="profile-name">{result.profile?.name || 'No resume parsed yet'}</p>
                  <p className="profile-role">{result.profile?.title || 'No explicit role title detected'}</p>
                </div>

                <div className="contact-stack">
                  {result.profile?.email ? (
                    <span>
                      <Mail size={14} />
                      {result.profile.email}
                    </span>
                  ) : null}
                  {result.profile?.phone ? (
                    <span>
                      <Phone size={14} />
                      {result.profile.phone}
                    </span>
                  ) : null}
                  {result.profile?.location ? (
                    <span>
                      <MapPin size={14} />
                      {result.profile.location}
                    </span>
                  ) : null}
                  {Object.entries(result.profile?.links || {}).map(([label, value]) => (
                    <a href={value} key={label} className="link-pill" target="_blank" rel="noreferrer">
                      {titleCase(label)}
                    </a>
                  ))}
                </div>
              </motion.div>

              <motion.div className="highlight-strip" variants={staggerContainer} initial="hidden" animate="show">
                <motion.article variants={softIn} whileHover={{ y: -3 }}>
                  <BriefcaseBusiness size={18} />
                  <strong>{result.highlights?.estimatedExperienceYears || 'Pending'}</strong>
                  <span>Experience signal</span>
                </motion.article>
                <motion.article variants={softIn} whileHover={{ y: -3 }}>
                  <GraduationCap size={18} />
                  <strong>{result.highlights?.educationLevel || 'Pending'}</strong>
                  <span>Education level</span>
                </motion.article>
                <motion.article variants={softIn} whileHover={{ y: -3 }}>
                  <Sparkles size={18} />
                  <strong>{result.highlights?.projectMentions ?? 0}</strong>
                  <span>Projects</span>
                </motion.article>
              </motion.div>

              <motion.div className="results-scroll" variants={staggerContainer} initial="hidden" animate="show">
                <motion.div className="content-block" variants={riseIn}>
                  <h3>Top skills</h3>
                  <div className="chip-wrap">
                    {(topSkills.length ? topSkills : ['No skills detected']).map((skill) => (
                      <motion.span className="chip" key={skill} variants={softIn}>
                        {skill}
                      </motion.span>
                    ))}
                  </div>
                </motion.div>

                <motion.div className="content-block" variants={riseIn}>
                  <h3>Skill buckets</h3>
                  {skillBuckets.length ? (
                    <div className="bucket-list">
                      {skillBuckets.map(([bucket, items]) => (
                        <motion.article key={bucket} variants={softIn}>
                          <span>{bucket.replace('_', ' ')}</span>
                          <p>{items.join(', ')}</p>
                        </motion.article>
                      ))}
                    </div>
                  ) : (
                    <p className="muted-copy">No categorized skill buckets were detected.</p>
                  )}
                </motion.div>

                <motion.div className="content-block" variants={riseIn}>
                  <h3>Structured extraction</h3>
                  {structuredSections.length ? (
                    <motion.div className="structured-section-list" variants={staggerContainer}>
                      {structuredSections.map((section) => renderStructuredSection(section))}
                    </motion.div>
                  ) : (
                    <p className="muted-copy">No structured sections are available yet.</p>
                  )}
                </motion.div>

                <motion.div className="content-grid" variants={staggerContainer}>
                  <motion.div className="content-block" variants={riseIn}>
                    <h3>Experience timeline</h3>
                    {result.experienceTimeline?.length ? (
                      <div className="timeline-list">
                        {result.experienceTimeline.map((item, index) => (
                          <motion.article key={`${item.dateRange}-${index}`} variants={softIn}>
                            <strong>{item.dateRange}</strong>
                            <p>{item.title || item.company || item.context}</p>
                            {item.title && item.company && item.title !== item.company ? (
                              <small>{item.company}</small>
                            ) : null}
                          </motion.article>
                        ))}
                      </div>
                    ) : (
                      <p className="muted-copy">Timeline extraction will appear here after parsing.</p>
                    )}
                  </motion.div>

                  <motion.div className="content-block" variants={riseIn}>
                    <h3>Learning and in-progress signals</h3>
                    {learningSignals.length ? (
                      <div className="learning-list">
                        {learningSignals.map((signal) => (
                          <motion.article key={`${signal.section}-${signal.group}-${signal.name}`} variants={softIn}>
                            <strong>{signal.name}</strong>
                            <p>
                              {signal.group} / {signal.section}
                            </p>
                            <small>{signal.status}</small>
                          </motion.article>
                        ))}
                      </div>
                    ) : (
                      <p className="muted-copy">Learning markers like `(learning)` or `(practicing)` will appear here.</p>
                    )}
                  </motion.div>
                </motion.div>

                <motion.div className="content-block" variants={riseIn}>
                  <h3>Parser insights</h3>
                  <ul className="insight-list">
                    {(result.insights?.length ? result.insights : ['Insights will be generated after parsing.']).map(
                      (insight) => (
                        <li key={insight}>{insight}</li>
                      ),
                    )}
                  </ul>
                </motion.div>
              </motion.div>
            </motion.section>
          )}
        </AnimatePresence>
      </section>

      <footer className="app-footer">
        <p>Engineered for builders turning resumes into recruiter-ready intelligence.</p>
        <a
          className="footer-link"
          href="https://github.com/lazy0ne369/ResumeParser_io.git"
          target="_blank"
          rel="noreferrer"
        >
          GitHub repo
        </a>
      </footer>
    </div>
  )
}

export default App
