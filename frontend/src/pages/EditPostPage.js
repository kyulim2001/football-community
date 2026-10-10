import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { useNavigate, useParams } from 'react-router-dom';
import styles from '../styles/CreatePostPage.module.scss';

function EditPostPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [existingFiles, setExistingFiles] = useState([]); // 기존 파일들
  const [deletedFileIds, setDeletedFileIds] = useState([]); // 삭제할 파일 ID
  const [newFiles, setNewFiles] = useState([]); // 새로 추가할 파일
  const [fileNames, setFileNames] = useState([]);

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const res = await api.get(`/api/posts/${id}/`);
        setTitle(res.data.title);
        setContent(res.data.content);
        setExistingFiles(res.data.media);
      } catch (err) {
        alert('게시글 정보를 불러오지 못했습니다.');
        navigate(-1);
      }
    };
    fetchPost();
  }, [id, navigate]);

  const handleDeletedFileChange = (fileId) => {
    setDeletedFileIds((prev) => [...prev, fileId]);
    setExistingFiles((prev) => prev.filter((file) => file.id !== fileId));
  };

  const handleRemoveNewFile = (index) => {
    setNewFiles((prev) => prev.filter((_, i) => i !== index));
    setFileNames((prev) => prev.filter((_, i) => i !== index));
  };

  const handleNewFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    const previewedFiles = selectedFiles.map(file => ({
      file,
      preview: URL.createObjectURL(file),
    }));
    setNewFiles((prev) => [...prev, ...previewedFiles]);
    setFileNames((prev) => [...prev, ...selectedFiles.map(file => file.name)]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content);
    formData.append('deleted_media_ids', JSON.stringify(deletedFileIds));
    newFiles.forEach(({ file }) => formData.append('files', file));

    try {
      await api.patch(`/api/posts/${id}/`, formData);
      alert('게시글이 수정되었습니다!');
      navigate(`/posts/${id}`);
    } catch (err) {
      alert('수정 실패: ' + (err.response?.data?.detail || '오류 발생'));
    }
  };

  return (
    <div className={styles.createPostPage}>
      <h2>게시글 수정</h2>
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

        {/* 기존 파일 목록 */}
        {existingFiles.length > 0 && (
          <div className={styles.mediaPreview}>
            <h4>기존 첨부파일</h4>
            {existingFiles.map((file) => (
              <div key={file.id} className={styles.mediaItem}>
                {file.file.endsWith('.mp4') ? (
                  <video src={file.file} controls />
                ) : (
                  <img src={file.file} alt="미리보기" />
                )}
                <button
                  type="button"
                  className={styles.deleteButton}
                  onClick={() => handleDeletedFileChange(file.id)}
                >
                  &times;
                </button>
              </div>
            ))}
          </div>
        )}

        {/* 새 파일 업로드 */}
        <div className={styles.fileInputWrapper}>
          <label htmlFor="fileUpload">파일 선택</label>
          <input
            id="fileUpload"
            type="file"
            accept="image/*,video/*"
            multiple
            onChange={handleNewFileChange}
          />
        </div>

        {/* 새로 선택한 파일 미리보기 */}
        {newFiles.length > 0 && (
          <div className={styles.mediaPreview}>
            <h4>새 첨부파일</h4>
            {newFiles.map((item, index) => (
              <div key={index} className={styles.mediaItem}>
                {item.file.type.startsWith('video') ? (
                  <video src={item.preview} controls />
                ) : (
                  <img src={item.preview} alt="미리보기" />
                )}
                <button
                  type="button"
                  className={styles.deleteButton}
                  onClick={() => handleRemoveNewFile(index)}
                >
                  &times;
                </button>
              </div>
            ))}
          </div>
        )}

        <button type="submit">수정하기</button>
      </form>
    </div>
  );
}

export default EditPostPage;
