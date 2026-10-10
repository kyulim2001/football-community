import React, { useState } from 'react';
import api from '../api/axios';
import { useNavigate, useParams } from 'react-router-dom';
import styles from '../styles/CreatePostPage.module.scss';

const leagueToId = {
  "premier-league": 3,
  "la-liga": 4,
  "bundesliga": 5,
  "serie-a": 6,
  "ligue-1": 7,
};

function CreatePostPage() {
  const { league } = useParams();
  const boardId = leagueToId[league];
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [files, setFiles] = useState([]);
  const navigate = useNavigate();

  if (!boardId) {
    alert('잘못된 게시판 경로입니다.');
    return <div>잘못된 접근입니다.</div>;
  }

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    const previewedFiles = selectedFiles.map(file => ({
      file,
      preview: URL.createObjectURL(file),
    }));
    setFiles(previewedFiles);
  };

  const handleFileDelete = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content);
    formData.append('board', Number(boardId));
    files.forEach(({ file }) => formData.append('files', file));

    try {
      const res = await api.post('/api/posts/', formData);
      alert('게시글이 작성되었습니다!');
      navigate(`/posts/${res.data.id}`);
    } catch (err) {
      alert('게시글 작성 실패: ' + (err.response?.data?.detail || '오류 발생'));
    }
  };

  return (
    <div className={styles.createPostPage}>
      <h2>게시글 작성</h2>
      <form className={styles.postForm} onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="제목"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <textarea
          placeholder="내용"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={6}
          required
        />

        {/* 파일 미리보기 */}
        {files.length > 0 && (
          <div className={styles.mediaPreview}>
            <h4>선택한 파일</h4>
            {files.map((item, index) => (
              <div key={index} className={styles.mediaItem}>
                {item.file.type.startsWith('video') ? (
                  <video src={item.preview} controls />
                ) : (
                  <img src={item.preview} alt="미리보기" />
                )}
                <button
                  type="button"
                  className={styles.deleteButton}
                  onClick={() => handleFileDelete(index)}
                >
                  &times;
                </button>
              </div>
            ))}
          </div>
        )}

        <div className={styles.fileInputWrapper}>
          <label htmlFor="fileUpload">파일 선택</label>
          <input
            id="fileUpload"
            type="file"
            accept="image/*,video/*"
            multiple
            onChange={handleFileChange}
          />
        </div>
        <button type="submit">작성하기</button>
      </form>
    </div>
  );
}

export default CreatePostPage;
