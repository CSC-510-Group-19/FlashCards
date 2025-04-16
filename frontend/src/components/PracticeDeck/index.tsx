import { Swiper, SwiperSlide } from "swiper/react";

import "swiper/css";
import "swiper/css/pagination";
import "swiper/css/navigation";

import "./styles.scss";

import { Pagination, Navigation } from "swiper";
import ReactCardFlip from "react-card-flip";
import { useEffect, useState } from "react";
import { useParams } from "react-router";
import http from "utils/api";
import { Progress } from "antd";

export default function Flashcard({cards}: any) {
  const { id } = useParams();
  const [studyTime, setStudyTime] = useState(0);
  const [activeGoal, setActiveGoal] = useState("");
  const idToken = window.localStorage.getItem('idToken');

  const idToken = window.localStorage.getItem('idToken')

  useEffect(() => {

    const fetchGoal = async () => {
      try {
        const res = await http.get(`/deck/goal/${id}`, {
        headers: {
          'Authorization': `${idToken}`
        }
      });
        setActiveGoal(res.data.goal || "");
      } catch (err) {
        console.error("Error fetching goal:", err);
      }
    };
    updateStreak();
    fetchGoal();
  }, [id]);
  useEffect(() => {
    if (activeGoal !== "Study this deck for 20 minutes") return;

    const startTime = Date.now();
    
    const interval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      setStudyTime(elapsed);

      // Send PATCH request every 5 seconds
      if (elapsed % 5 === 0) {
        updateStudyGoal(5);
      }
    }, 5000);

    return () => {
      clearInterval(interval);
      updateStudyGoal(studyTime);
    };
  }, [activeGoal]);

  const updateStudyGoal = async (elapsedTime: number) => {
    try {
      await http.patch(`/deck/goal/${id}`, {
        goalType: "Study this deck for 20 minutes", // Send goal type
        progress: elapsedTime,
      }, {
        headers: {
          'Authorization': `${idToken}`
        }
      });
      console.log("Study goal updated:", elapsedTime);
    } catch (err) {
      console.error("Error updating study goal:", err);
    }
  };

  const updateStreak = async () => {
    try {
      await http.patch(`/deck/streak/${id}`, {}, {
        headers: {
          'Authorization': `${idToken}`
        }
      });
      console.log("Streak updated successfully");
    } catch (err) {
      console.error("Error updating streak:", err);
    }
  };

  return (
    <>
      <Swiper
        pagination={{
          type: "progressbar",
        }}
        navigation={true}
        modules={[Pagination, Navigation]}
        className="mySwiper"
      >
        {cards.map(({ front, back, hint }: any, index: number) => {
          return (
            <SwiperSlide>
              <Card
                index={index}
                total={cards.length}
                front={front}
                back={back}
              />
            </SwiperSlide>
          );
        })}
        <SwiperSlide>
          <div className="card-item final-view">
            <div>
              <p>Yaaay! You have come to the end of your practice 🎉🎊</p>
            </div>
          </div>
        </SwiperSlide>
      </Swiper>
    </>
  );
}

const Card = ({ front, back, index, total }: any) => {
  const [isFlipped, setIsFlipped] = useState(false);
  return (
    <ReactCardFlip isFlipped={isFlipped} flipDirection="vertical">
      <div className="card-item" onClick={() => setIsFlipped(!isFlipped)}>
        <div>
          <p>Front</p>
          <h2>{front}</h2>
        </div>
        <div className="bottom">
            <p>{index + 1} / {total}</p>
        </div>
      </div>
      <div className="card-item" onClick={() => setIsFlipped(!isFlipped)}>
        <div>
          <p>Back</p>
          <h2>{back}</h2>
        </div>
        <div className="bottom">
            <p>{index + 1} / {total}</p>
        </div>
      </div>
    </ReactCardFlip>
  );
};
