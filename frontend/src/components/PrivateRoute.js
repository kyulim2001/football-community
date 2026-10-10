import React from 'react';
import { Navigate } from 'react-router-dom'; // 페이지를 강제로 이동 시킬때 사용
import { useRecoilValue } from 'recoil';  // 읽기 전용
import { userState } from '../recoil/atoms'; // 전역 상태를 읽어옴

const PrivateRoute = ({ children }) => { 
    const user = useRecoilValue(userState); // 현재 정보를 읽어옴

    if (!user.isLoggedIn) {
        return <Navigate to="/login" replace />;
    }
    return children;
};

export default PrivateRoute;