import axios from "axios";
import React from "react";
import { useNavigate } from "react-router-dom";

const StoryGenerator = () => {
  const navigate = useNavigate();
  const [theme, setTheme] = useState("");
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let pollInterval;

    if (jobId && jobStatus === "processing") {
      pollInterval = setInterval(() => {
        pollJobStatus(jobId);
      }, 3000);
    }

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [jobId, jobStatus]);

  const generateStory = async (theme) => {
    setLoading(true);
    setError(null);
    setTheme(theme);

    try {
      const response = await axios.post(`${API_BASE_URL}/stories/crate`, {
        theme,
      });

      const { job_id, status } = response.data;

      setJobId(job_id);
      setJobStatus(status);

      pollJobStatus(job_id);
    } catch (e) {
      setLoading(false);
      setError(`Failed to generate story: ${e.message}`);
    }
  };

  const pollJobStatus = async (id) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/jobs/${id}`);
      const { status, story_id, error: jobError } = response.data;

      if (status === "completed" && story_id) {
        fetchStory(story_id);
      } else if (status === "failed" && jobError) {
        setError(jobError || "An error occurred while generating the story");
        setLoading(false);
      }
    } catch (e) {
      if (e.response?.status !== 404) {
        setError(`Failed to poll job status: ${e.message}`);
        setLoading(false);
      }
    }
  };

  const fetchStory = async (id) => {
    // here we call this as soon as the job is finished and the story is ready
    try {
      setLoading(false);
      setJobStatus("completed");
      navigate(`/story/${id}`);
    } catch (e) {
      setError(`Failed to load story: ${e.message}`);
      setLoading(false);
    }
  };

  const reset = () => {
    setTheme("");
    setJobId(null);
    setJobStatus(null);
    setError(null);
    setLoading(false);
  };

  return (
    <div className="story-generator">
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={reset}>Try Again</button>
        </div>
      )}
      {!jobId && !error && !loading && <ThemeInput onSubmit={generateStory} />}
      {loading && <LoadingStatus theme={theme} />}
    </div>
  );
};

export default StoryGenerator;
