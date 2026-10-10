import React from "react";
import {Link, Outlet, useLocation} from "react-router-dom";
import styles from '../../styles/MyPage.module.scss';

const MyPage = () => {
    const location = useLocation(); // 현재 브라우저 url 경로 정보를 담고 있는 객체, 탭이 현재 선택된 상태인지 확인할 때 사용

    const tabList = [
        {name: "작성글", path: "posts"},
        {name: "작성댓글", path: "comments"},
        {name: "좋아요한 글", path: "likes"},
        {name: "비밀번호 변경", path: "password"},
        {name: "회원 탈퇴", path: "delete"}, 
        {name: "내 정보", path: "info"},
    ]; // 탭 목록 배열, 각 탭에 표시될 이름과 하위 경로
    return (
    <div className={styles.container}>
        <h2 className={styles.heading}>마이페이지</h2>
        <nav className={styles.tabNav}>
        {tabList.map((tab) => {
            const isActive = location.pathname.includes(`/mypage/${tab.path}`);
            return (
            <Link
                key={tab.path}
                to={tab.path}
                className={`${styles.tabLink} ${isActive ? styles.active : ''}`}
            >
                {tab.name}
            </Link>
            );
        })}
        </nav>
        <Outlet />
    </div>
    );
};


export default MyPage;