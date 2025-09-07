import { useState, useEffect, startTransition } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import LoadingStatus from "./LoadingStatus.jsx";
import StoryGame from "./StoryGame.jsx";
import { API_BASE_URL } from "../util.js";

const StoryLoader = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [story, setStory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadStory = async (storyId) => {
    setLoading(true);
    setError(null);

    useEffect(() => {
      loadStory(id);
    }, [id]);

    try {
      const response = await axios.get(
        `${API_BASE_URL}/stories/${storyId}/complete`
      );
      setStory(response.data);
      startTransition(() => navigate(`/story/${storyId}`));
    } catch (error) {
      if (error.response && error.response.status === 404) {
        setError("Story not found");
      } else {
        setError("An error occurred while loading the story");
      }
    } finally {
      setLoading(false);
    }
  };

  const createNewStory = () => {
    navigate("/");
  };

  if (loading) return <LoadingStatus theme="story" />;

  if (error)
    return (
      <div className="story-loader">
        <div className="error-message">
          <h2>Story Not Found</h2>
          <p>{error}</p>
          <button onClick={createNewStory}>Create New Story</button>
        </div>
      </div>
    );

  if (story) {
    return (
      <div className="story-loader">
        <StoryGame story={story} onNewStory={createNewStory} />
      </div>
    );
  }
};

export default StoryLoader;
